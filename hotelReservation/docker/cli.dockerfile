FROM cc-uservice-security/sof_root:0.1.12 as root
FROM cc-uservice-security/base:0.2.1

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    luarocks \
    python3-click \
    python3-cryptography \
    python3-dev \
    python3-jinja2 \
    python3-protobuf \
    python3-pyelftools \
    python3-pip \
    python3.8-venv \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --no-cache-dir 'toml>=0.10'

# Configure Lua
RUN luarocks install luasocket

# Configure development enviornment
COPY --from=root /usr/local/bin/nvim /usr/local/bin/nvim
COPY --from=root /usr/local/share/nvim /usr/local/share/nvim
RUN curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim \
    && GOBIN=/usr/local/go/bin \
    /usr/local/go/bin/go install golang.org/x/tools/gopls@latest
WORKDIR /root/dotfiles/nvim
COPY  dev/nvim /root/dotfiles/nvim
WORKDIR /root/.config/nvim
RUN ln -s /root/dotfiles/nvim/init.vim /root/.config/nvim/init.vim \
    && ln -s /root/dotfiles/nvim/after /root/.config/nvim/ \
    && ln -s /root/dotfiles/nvim/syntax /root/.config/nvim/ \
    && nvim +PlugInstall +qa \
    && nvim +PlugUpdate +qa
COPY dev/.bashrc /root/.bashrc

# Get the benchmark code
COPY dev/netrc_intel /root/.netrc
ARG DSB_VERSION
WORKDIR /code
RUN git clone \
    -b v${DSB_VERSION} \
    https://github.com/lsds/cc-DeathStarBench.git \
    DeathStarBench
WORKDIR /code/DeathStarBench/hotelReservation

ENV DSB_DOCKER="on"

# Python set-up
RUN ./bin/create_venv.sh

# Build native targets
RUN source venv/bin/activate && inv dev.build --runtime native

# Build EGo targets
# TODO(carlosse): annoyingly, EGo requires all env. variables for the enclave
# to be provided at build time. To deploy on Kubernetes we rely on the binaries
# packaged in the containers, and Consul support depends on an env. variable
# that we set at runtime. As a consequence, as it stands now, we can not have
# an EGo deployment that runs both with and without Consul in the same docker
# image tag.
RUN source venv/bin/activate \
    && ENABLE_CONSUL=off inv dev.build --runtime ego dev.build --runtime gramine

RUN echo ". /code/DeathStarBench/hotelReservation/bin/workon.sh" >> /root/.bashrc
