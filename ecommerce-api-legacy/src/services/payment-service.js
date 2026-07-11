function processPayment(cardNumber) {
    return cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
}

module.exports = { processPayment };
