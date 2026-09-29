# Small helpers shared by the methodology's notebook/analysis pages.
# Included from a page with: include('src/method/py/utils.py')

def frag(iri):
    """Local name of an IRI (after the last # or /)."""
    return (iri or '').rstrip('/').split('#')[-1].split('/')[-1]

def display_label(label, iri):
    """Prefer an explicit rdfs:label, fall back to the IRI fragment."""
    return label or frag(iri)

def image_html(fig):
    """Render a matplotlib figure as an inline PNG so display() can show it."""
    import io, base64
    import matplotlib.pyplot as plt  # type: ignore
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f'<img src="data:image/png;base64,{b64}" style="max-width:100%;border-radius:4px">'
