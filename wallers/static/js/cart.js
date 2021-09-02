var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        var amount;
        if(action == 'add_mulitple'){
            amount = document.getElementById(productId).value
        }
        
        if(user == "AnonymousUser"){
            addCookieItem(productId, action, parseInt(amount))
        } else {
            updateUserOrder(productId, action, parseInt(amount))
        }
    })
}

function addCookieItem(productId, action, amount){

    if(action == 'add'){
        if(cart[productId] == undefined) {
            cart[productId] = {'quantity':1}
        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if(action == 'add_mulitple'){
        if(cart[productId] == undefined) {
            cart[productId] = {'quantity': amount}
        } else {
            cart[productId]['quantity'] += amount
        }
        
    }

    if(action == 'remove') {
        cart[productId]['quantity'] -= 1

        if(cart[productId]['quantity'] <= 0) {
            delete cart[productId]
        }
    }

    if(action == 'delete') {
        cart[productId]['quantity'] = 0

        if(cart[productId]['quantity'] <= 0) {
            delete cart[productId]
        }
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}

function updateUserOrder(productId, action, amount) {

    var url = 'update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'productId': productId, 'action': action, 'amount': amount})  
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        location.reload()
    })

}