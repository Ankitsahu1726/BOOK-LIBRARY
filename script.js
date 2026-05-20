console.log("Book Library App Loaded Successfully");

const buttons = document.querySelectorAll('button');

buttons.forEach(button => {
    button.addEventListener('click', () => {
        console.log(`${button.innerText} button clicked`);
    });
});