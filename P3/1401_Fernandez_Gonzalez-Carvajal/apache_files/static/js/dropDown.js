$(document).ready(function(){
    $(".dropDown").find('p').click(function(){
        $(this).parent().find('.dropDownContent').toggle();
    });
});
