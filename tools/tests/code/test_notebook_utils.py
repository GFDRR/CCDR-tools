from tools.code.notebook_utils import create_header_widget
from ipywidgets import HTML


def test_create_header_widget():
        
    widget = create_header_widget('tools/code/rdl_logo.png')
    assert isinstance(widget, HTML)

    # Check if the HTML content contains the expected elements and styles
    html_elems = [
        "background: linear-gradient(to bottom, #003366, transparent);",
        "padding: 20px;",
        "border-radius: 10px 10px 0 0;",
        "display: flex;",
        "justify-content: space-between;",
        "align-items: center;",
        "width: 100%;",
        "box-sizing: border-box;",
        "overflow: hidden;"
    ]
    
    for elem in html_elems:
        assert elem in widget.value
