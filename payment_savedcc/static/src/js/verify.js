$("input[name='ccNumber']")[0].setCustomValidity('Empty');
$("input[name='ccName']")[0].setCustomValidity('Empty');
$("input[name='ccDate']")[0].setCustomValidity('Empty');

function checkInput(){
    return ($("input[name='ccNumber']")[0].checkValidity() && $("input[name='ccName']")[0].checkValidity() && $("input[name='ccDate']")[0].checkValidity())
}

$("input[name='ccNumber']").validateCreditCard(
    function(result){
        if (result.card_type != null){
            $("select[name='ccType']").val(result.card_type.name);
        }
        if (result.length_valid && result.luhn_valid){
            $("input[name='ccNumber']")[0].setCustomValidity('');
        }else{
            $("input[name='ccNumber']")[0].setCustomValidity('ErrCC');
        }
        if (checkInput()){
            $("button[name='ccSub']").removeAttr("disabled");
        }else{
            $("button[name='ccSub']").attr("disabled","disabled");
        }
    }, {
        accept: ['visa', 'mastercard']
    }
);
$("input[name='ccName']").on('input',
    function(){
        if ($(this).val().length > 2){
            $(this)[0].setCustomValidity('');
        }else{
            $(this)[0].setCustomValidity('ErrName');
        }
        if (checkInput()){
            $("button[name='ccSub']").removeAttr("disabled");
        }else{
            $("button[name='ccSub']").attr("disabled","disabled");
        }
    }
);
$("input[name='ccDate']").on('input',
    function(){
        if ($(this).val().length >= 5){
            $(this)[0].setCustomValidity('');
        }else{
            $(this)[0].setCustomValidity('ErrDate');
        }
        if (checkInput()){
            $("button[name='ccSub']").removeAttr("disabled");
        }else{
            $("button[name='ccSub']").attr("disabled","disabled");
        }
    }
);