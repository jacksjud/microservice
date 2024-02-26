/* 
Example of implementation of using the microservice on browser

- Browser side

*/
const button = document.getElementById("example")
button.addEventListener("click", () => {
    console.log("== Button Clicked")
    fetch('/microservice/data')
        .then(response => response.json())
        .then(data => {
            console.log("Here is the data: ", data)
        })
        .catch(error => {
            console.log("Error getting data: ", error)
        })
})
