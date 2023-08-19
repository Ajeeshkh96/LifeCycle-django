/* Assign actions */
$(document).on('change', '.product-quantity input', function() {
  updateQuantity(this);
});

$(document).on('click', '.product-removal button', function() {
  removeItem(this);
});

/* Recalculate cart */
function recalculateCart() {
  var subtotal = 0;

  /* Sum up row totals */
  $('.product').each(function() {
    var price = parseFloat($(this).find('.product-price').text().replace('₹', ''));
    var quantity = parseInt($(this).find('.product-quantity input').val());
    var linePrice = price * quantity;
    $(this).find('.product-line-price').text('₹' + linePrice.toFixed(2));
    subtotal += linePrice;
  });

  /* Calculate totals */
  var tax = subtotal * taxRate;
  var shipping = (subtotal > 0 ? shippingRate : 0);
  var total = subtotal + tax + shipping;

  /* Update totals display */
  $('.totals-value').fadeOut(fadeTime, function() {
    $('#cart-subtotal').text('₹' + subtotal.toFixed(2));
    $('#cart-tax').text('₹' + tax.toFixed(2));
    $('#cart-shipping').text('₹' + shipping.toFixed(2));
    $('#cart-total').text('₹' + total.toFixed(2));
    if (total == 0) {
      $('.checkout').fadeOut(fadeTime);
    } else {
      $('.checkout').fadeIn(fadeTime);
    }
    $('.totals-value').fadeIn(fadeTime);
  });
}

/* Update quantity */
function updateQuantity(quantityInput) {
  var productRow = $(quantityInput).closest('.product');
  var price = parseFloat(productRow.find('.product-price').text().replace('₹', ''));
  var quantity = parseInt($(quantityInput).val());
  var linePrice = price * quantity;
  productRow.find('.product-line-price').text('₹' + linePrice.toFixed(2));
  recalculateCart();
}

/* Remove item from cart */
function removeItem(removeButton) {
  var productRow = $(removeButton).closest('.product');
  productRow.slideUp(fadeTime, function() {
    productRow.remove();
    recalculateCart();
  });
}
