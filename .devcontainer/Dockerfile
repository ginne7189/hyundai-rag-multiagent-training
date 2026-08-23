FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# The upstream image can retain a Yarn APT source whose signing key has
# expired. The course does not use Yarn, and the stale source prevents the
# official sshd feature from installing during a clean Codespaces rebuild.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    /etc/apt/sources.list.d/yarn.sources
