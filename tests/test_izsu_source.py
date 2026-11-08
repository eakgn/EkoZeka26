"""İZSU canlı/offline fallback zinciri testleri (`test_izsu_source.py`)."""

from __future__ import annotations

import shutil

import pytest

import ekozeka26.izsu_source as src
from ekozeka26.data_pipeline import RAW_DIR


def test_live_parser_and_merge_preserves_verified_layers() -> None:
    base = src.load_izsu_snapshot(prefer_live=False)
    assert len(base["dams"]) == 5
    assert base["source_mode"] in {"live_cache", "verified_snapshot", "fallback_snapshot"}

    html = (RAW_DIR / "izsu.html").read_text(encoding="utf-8", errors="ignore")
    today, last_year = src._parse_live_html(html)
    assert len(today) == 5

    merged = src._merge_live(
        base, today, last_year, fetched_at="2026-11-08T00:00:00+00:00"
    )
    assert merged["source_mode"] == "live_fetch"
    assert len(merged["dams"]) == 5
    assert abs(merged["headline_metrics"]["capacity_weighted_occupancy_pct"] - 34.01) < 0.1
    # Canlı baraj sayfası aylık üretim/tarife içermez; doğrulanmış katman korunmalı.
    assert merged["monthly_production_2025"]
    assert merged["tariffs_2026"]


def test_fallback_chain_when_processed_snapshot_is_corrupt(tmp_path, monkeypatch) -> None:
    processed = tmp_path / "processed" / "izsu_snapshot.json"
    fallback = tmp_path / "fallback" / "izsu_snapshot.json"
    live_cache = tmp_path / "izsu_live_snapshot.json"
    processed.parent.mkdir(parents=True)
    fallback.parent.mkdir(parents=True)
    processed.write_text("{bozuk-json", encoding="utf-8")
    shutil.copy(src.FALLBACK_DIR / "izsu_snapshot.json", fallback)

    monkeypatch.setattr(src, "_PROCESSED_PATH", processed)
    monkeypatch.setattr(src, "_FALLBACK_PATH", fallback)
    monkeypatch.setattr(src, "LIVE_CACHE_PATH", live_cache)

    snapshot = src.load_izsu_snapshot(prefer_live=False)
    assert snapshot["source_mode"] == "fallback_snapshot"
    assert len(snapshot["dams"]) == 5
    assert "doğrulanmış snapshot yok/geçersiz" in (snapshot["fallback_reason"] or "")


def test_all_sources_missing_raises_clear_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(src, "_PROCESSED_PATH", tmp_path / "yok.json")
    monkeypatch.setattr(src, "_FALLBACK_PATH", tmp_path / "yok2.json")
    monkeypatch.setattr(src, "LIVE_CACHE_PATH", tmp_path / "yok3.json")

    with pytest.raises(FileNotFoundError, match="İZSU snapshot bulunamadı"):
        src.load_izsu_snapshot(prefer_live=False)
