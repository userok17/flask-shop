$('.add_to_cart').submit(function(e){
    e.preventDefault();
    var $self = $(this);
    var str = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "/cart/add/?html=1",
        data: str,
        dataType: 'json',
        success: function(data){
            if(data['status'] == 'ok'){
                // Добавление количество выбранных товаров
                $('#count').text(data['count']);
                // Полная сумма выбранных товаров
                $('#total').text(data['total'].toFixed(2));
                // Анимация
                var cart = $('#cart');
                var temp_submit = $self.find('#submit').clone().appendTo('body');
                temp_submit.css({
                    'position' : 'absolute',
                    'z-index' : '10000',
                    'left': $self.find('#submit').offset().left,
                    'top': $self.find('#submit').offset().top,
                    'opacity': '0.7'
                });
                temp_submit.animate({
                    'top': cart.offset().top,
                    'left': cart.offset().left
                }, 'normal', function(){
                    $(this).remove();
                });
            }
        },
        error: function(msg){
            alert(msg);
        }
    });

});