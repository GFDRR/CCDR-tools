from tools.code.notebook_utils import create_header_widget
from ipywidgets import HTML


def test_create_header_widget():
        
    widget1 = create_header_widget(hazard="FL", img_path='tools/code/rdl_logo.png')
    assert isinstance(widget1, HTML)

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
        assert elem in widget1.value

    assert "FLOOD HAZARD (FATHOM 3)" in widget1.value
    
    widget2 = create_header_widget(hazard="TC", img_path='tools/code/rdl_logo.png')
    assert isinstance(widget2, HTML)
    for elem in html_elems:
        assert elem in widget2.value
    assert "TROPICAL CYCLONE HAZARD (STORM v4)" in widget2.value