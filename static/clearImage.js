$(function(){
      
window.resetFile = function (e) {
    e.wrap('<form>').closest('form').get(0).reset();
    e.unwrap();
}

    });