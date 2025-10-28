# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2024-XX-XX

### Added
- **Areios Pagos Crawler** (`scripts/areiospagos_crawler.py`) - Discovers decision codes from Greek Supreme Court
- **HTML Encoding Fixers** - Fix encoding issues in HTML files:
  - `fix_html_encoding.py` - Basic encoding fix (cp1253/iso-8859-7 → UTF-8)
  - `fix_html_encoding_advanced.py` - Advanced fix with gzip and Mojibake detection

## [0.4.0] - 2024-XX-XX

### Added
- **Mantinades.gr Downloader** (`scripts/mantinades_downloader.py`) - Cretan mantinades downloader
- **EKDD Materials Downloader** (`scripts/ekdd_downloader.py`) - Educational materials from resources.ekdd.gr
- **Poets.gr Downloader** (`scripts/poets_gr_downloader.py`) - Poems from poets.gr
- **PDF to Text Converter** (`scripts/pdf_to_text.py`) - PDFs to markdown using pymupdf4llm
- Comprehensive documentation for all new tools

### Changed
- Updated README with complete pipeline overview
- Updated architecture documentation

## [0.3.0] - 2024-XX-XX

### Added
- **MinHash Deduplication Pipeline** using DataTrove
- 4-stage deduplication process (signatures, buckets, clusters, filter)
- Statistics generation by source
- Configuration management via `config/pipeline_conf.py`
- Detailed deduplication documentation in `scripts/deduplication/README.md`

### Changed
- Updated requirements.txt with DataTrove, spaCy, transformers, pandas

## [0.2.0] - 2024-XX-XX

### Added
- **Podcast Transcription** (`scripts/transcribe_podcasts.sh`) - Automated transcription using Whisper
- GPU acceleration support for transcription
- Multiple audio format support (mp3, m4a, wav, flac, ogg, webm, wma, aac)
- Automatic skip functionality for already-processed files
- Professional repository structure with proper directory organization

### Changed
- Reorganized repository with scripts/, config/, docs/, data/ directories
- Enhanced README with comprehensive documentation

## [0.1.0] - 2024-XX-XX

### Added
- Initial release with ELSYN downloader
- Selenium-based automation for downloading anonymized legal decisions
- Resume functionality with progress tracking
- Manual filter support
- Smart pagination
- GitHub SSH integration
- MIT License
- Contributing guidelines

[0.5.0]: https://github.com/mersinkonomi/greek_llm_pipeline/tree/v0.5.0
[0.4.0]: https://github.com/mersinkonomi/greek_llm_pipeline/tree/v0.4.0
[0.3.0]: https://github.com/mersinkonomi/greek_llm_pipeline/tree/v0.3.0
[0.2.0]: https://github.com/mersinkonomi/greek_llm_pipeline/tree/v0.2.0
[0.1.0]: https://github.com/mersinkonomi/greek_llm_pipeline/tree/v0.1.0
