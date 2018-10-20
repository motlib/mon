
/* Function to return a single element by xpath expression. */
var get_element = function(root, exp) {
    return document.evaluate(
        exp,
        root,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

/* Function to expand / collape a toolbox when clicking the toolbox
 * heading. */
var toggle_content = function(el_h) {
    var el_content = get_element(el_h, "../div[@class='content']")
    var el_tglind = get_element(el_h, "span[@class='tglind']")

    if(el_content.style.display == 'none') {
        el_content.style.display = 'block';
        el_tglind.innerHTML = '[-]';
    } else {
        el_content.style.display = 'none';
        el_tglind.innerHTML = '[+]';
    }
}
