$(document).ready(function() {
    $("#login").validate({
        rules:{
            email:{
                required:true,
                email: true
            },
            passwd:{
                required:true,
            }
        },
        errorClass: "help-inline"
    });
});