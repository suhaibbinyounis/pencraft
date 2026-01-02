"""Tests for configuration settings."""

from openblog.config.settings import Settings, load_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self) -> None:
        """Test default settings values."""
        settings = Settings()

        assert settings.llm.base_url == "http://localhost:3030"
        assert settings.llm.model is not None  # Model can vary based on env
        assert settings.llm.temperature == 0.7
        assert settings.llm.max_tokens == 4096

        assert settings.research.max_search_results == 10
        assert settings.research.max_sources == 5

        assert settings.blog.min_word_count == 1500
        assert settings.blog.include_toc is True
        assert settings.blog.include_citations is True

    def test_custom_settings(self) -> None:
        """Test custom settings values."""
        settings = Settings(
            llm={
                "base_url": "http://custom:8080",
                "model": "custom-model",
                "temperature": 0.5,
            },
            blog={
                "min_word_count": 3000,
            },
        )

        assert settings.llm.base_url == "http://custom:8080"
        assert settings.llm.model == "custom-model"
        assert settings.llm.temperature == 0.5
        assert settings.blog.min_word_count == 3000

    def test_settings_to_dict(self) -> None:
        """Test converting settings to dictionary."""
        settings = Settings()
        data = settings.to_dict()

        assert "llm" in data
        assert "research" in data
        assert "output" in data
        assert "hugo" in data
        assert "blog" in data
        assert data["llm"]["base_url"] == "http://localhost:3030"

    def test_load_settings(self) -> None:
        """Test load_settings function."""
        settings = load_settings(verbose=True)

        assert settings.verbose is True


class TestLLMSettings:
    """Test cases for LLM settings."""

    def test_temperature_bounds(self) -> None:
        """Test temperature validation bounds."""
        # Valid temperature
        settings = Settings(llm={"temperature": 1.5})
        assert settings.llm.temperature == 1.5

    def test_api_key_default(self) -> None:
        """Test default API key."""
        settings = Settings()
        assert settings.llm.api_key == "dummy-api-key"


class TestHugoSettings:
    """Test cases for Hugo settings."""

    def test_default_frontmatter(self) -> None:
        """Test default frontmatter values."""
        settings = Settings()

        assert settings.hugo.frontmatter_format == "yaml"
        assert isinstance(settings.hugo.default_frontmatter, dict)

    def test_custom_frontmatter(self) -> None:
        """Test custom frontmatter values."""
        settings = Settings(
            hugo={
                "frontmatter_format": "toml",
                "default_frontmatter": {"author": "Test"},
            }
        )

        assert settings.hugo.frontmatter_format == "toml"
        assert settings.hugo.default_frontmatter["author"] == "Test"
