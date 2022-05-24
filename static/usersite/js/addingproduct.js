var updateBtns = document.getElementsByClassName('update-cart')
var csrftoken = document.getElementsByName('csrfmiddlewaretoken')
var csrf_token = csrftoken[0].value;
for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product
        var action = this.dataset.action
        if (user == "AnonymousUser") {
            console.log('here')
            updateNonUserOrder(productId, action)
        } else {
            console.log(csrf_token)
            updateUserOrder(productId, action)
        }
    })
}

function updateNonUserOrder(procuctId, action) {
    if (action == 'add') {
        if (cart[procuctId] == undefined) {
            console.log("Not logged in")
            cart[procuctId] = { 'quantity': 1 }
            console.log('Cart : ', cart)
        } else {
            cart[procuctId]['quantity'] += 1
        }
    }
    if (action == 'sub') {
        cart[procuctId]['quantity'] -= 1
    }
    if (cart[procuctId]['quantity'] <= 0 || action == 'remove') {
        delete cart[procuctId]
    }
    console.log('Cart : ', cart)
    document.cookie = 'cart = ' + JSON.stringify(cart) + ";domain=;path=/"

}

function updateUserOrder(procuctId, action) {
    console.log("user is loged in sending data")
    var url = 'https://morning-reaches-68242.herokuapp.com/update'
    fetch(url, {

            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,

            },
            body: JSON.stringify({ 'productId': procuctId, 'action': action })
        })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('Data:', data)
        })
    location.reload()
}