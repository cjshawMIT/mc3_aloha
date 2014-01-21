$(document).ready(function() {
    $("#signup").validate({
        rules:{
            tos: {
                required:true
            },
            email:{
                required:true,
                email: true
            },
            passwd:{
                required:true,
                minlength: 8
            },
            conpasswd:{
                required:true,
                equalTo: "#passwd"
            }
        },
        errorClass: "help-inline"
    });
});