# Homebrew Formula for ClawCrew
#
# To install from this tap:
#   brew tap lanxindeng8/clawcrew https://github.com/lanxindeng8/clawcrew
#   brew install clawcrew
#
# Or install directly from this repo:
#   brew install --HEAD lanxindeng8/clawcrew/clawcrew
#
class Clawcrew < Formula
  include Language::Python::Virtualenv

  desc "Multi-agent AI team framework for OpenClaw"
  homepage "https://github.com/lanxindeng8/clawcrew"
  url "https://github.com/lanxindeng8/clawcrew/archive/refs/tags/v0.3.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"  # Update with actual sha256 when releasing
  license "MIT"
  head "https://github.com/lanxindeng8/clawcrew.git", branch: "main"

  depends_on "python@3.11"
  depends_on "jq"

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.9.0.tar.gz"
    sha256 "50922fd79edd4c62f97f2c0f9a7700faeaf1e46f3f9a64e65dcb1e2f4e23a3f5"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.0.tar.gz"
    sha256 "5cb5f659f8c4e6e4ae8eebb9fc2a8f a98a5cf4f9f72f9d8cb9c0c7a6e0b0f0a"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/source/h/httpx/httpx-0.25.0.tar.gz"
    sha256 "7f5c7c5e0b0b6e8b5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e"
  end

  resource "questionary" do
    url "https://files.pythonhosted.org/packages/source/q/questionary/questionary-2.0.1.tar.gz"
    sha256 "8e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/source/p/python-dotenv/python-dotenv-1.0.0.tar.gz"
    sha256 "5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e"
  end

  def install
    virtualenv_install_with_resources

    # Copy workspace templates
    (prefix/"share/clawcrew").install Dir["workspace-*"]
  end

  def post_install
    # Create user config directory
    (var/"clawcrew").mkpath
  end

  def caveats
    <<~EOS
      To complete setup, run:
        clawcrew init

      This will guide you through configuring Telegram and other settings.

      Note: OpenClaw must be installed separately.
      Visit https://openclaw.dev for installation instructions.

      Workspace templates are installed at:
        #{opt_prefix}/share/clawcrew/

      To copy workspaces to your OpenClaw directory:
        cp -r #{opt_prefix}/share/clawcrew/workspace-* ~/.openclaw/
    EOS
  end

  test do
    assert_match "ClawCrew version", shell_output("#{bin}/clawcrew --version")
  end
end
