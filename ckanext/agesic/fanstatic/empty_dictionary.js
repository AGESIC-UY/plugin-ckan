$(function() {
    if($("#data-dictionary table tbody tr").length == 0){
        $("#data-dictionary").toggle();
    }
    // find style-mark and apply missing classes to set the correct padding
    $("a[title=style-mark]").parents("div").first().addClass("u-p2 u-pt3");
});