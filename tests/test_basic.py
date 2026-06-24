import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestEmbeds:
    def test_import(self):
        from src import embeds

    def test_required_keys(self):
        from src.embeds import EMBED_URLS
        assert {"mcws","fifa","future_gms","naffl"}.issubset(EMBED_URLS.keys())

    def test_mcws_not_empty(self):
        from src.embeds import EMBED_URLS
        assert EMBED_URLS["mcws"]

    def test_iframe_returns_string(self):
        from src.embeds import iframe_html
        assert "iframe" in iframe_html("https://example.com")

    def test_empty_src_placeholder(self):
        from src.embeds import iframe_html
        assert "not configured" in iframe_html("").lower()

class TestPageFiles:
    def test_pages_dir_exists(self):
        assert os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "pages"))

    def test_page_files_present(self):
        pages = os.listdir(os.path.join(os.path.dirname(__file__), "..", "pages"))
        for prefix in ["1_FIFA","2_Mens","3_Future","4_NAFFL","5_About","6_Giving"]:
            assert any(p.startswith(prefix) for p in pages)

class TestDeployArtifacts:
    ROOT = os.path.join(os.path.dirname(__file__), "..")
    def test_procfile(self):
        assert "streamlit run app.py" in open(os.path.join(self.ROOT,"Procfile")).read()
    def test_render_yaml(self):
        assert os.path.isfile(os.path.join(self.ROOT,"render.yaml"))
    def test_streamlit_config(self):
        assert os.path.isfile(os.path.join(self.ROOT,".streamlit","config.toml"))
