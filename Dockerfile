FROM mambaorg/micromamba

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

RUN micromamba run pip install jupyter-cadquery
RUN micromamba run pip install cad-viewer-widget
RUN micromamba run pip install cairosvg
RUN micromamba run pip install imageio

# Delete this when ezdfx package is patched up
COPY patch_queryparser.py /opt/conda/lib/python3.13/site-packages/ezdxf/queryparser.py

USER mambauser
