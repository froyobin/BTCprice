// Our labels along the x-axis
var Time = ["19:47:40"];
// For drawing the lines
var btc = [75022];
var asia = [282,350,411,502,635,809,947,1402,3700,5267];
var europe = [168,170,178,190,203,276,408,547,675,734];
var latinAmerica = [40,20,10,16,24,38,74,167,508,784];
var northAmerica = [6,3,2,2,7,26,82,172,312,433];

var ctx = document.getElementById("myChart");
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: Time,
    datasets: [

      {
  data: btc,
  label: "BTC",
  borderColor: "#3e95cd",
  fill: false
},
// {
//   data: asia,
//   label: "Asia",
//   borderColor: "#3e95cd",
//   fill: false
// }
    ]
  }
});


/*Function to update the bar chart*/
function updateBarGraph(chart, data) {
  chart.data.datasets.pop();
  
  chart.data.datasets.push(
          {
  data: btc,
  label: "BTC",
  borderColor: "#3e95cd",
  fill: false
}  

    );
    chart.update();
}




/*Updating the bar chart with updated data in every second. */
setInterval(function () {
  
fetch('https://127.0.0.1:4356')
  .then(function(response) {
    return response.json();
  })
  .then(function (myJson) {
    
    obj = JSON.parse(JSON.stringify(myJson));
   
    if (Time.length > 24 * 60){
      Time = Time.shift()
      Time.push(obj.time)
      btc = btc.shift()
      btc.push(obj.price)
    }else{
      btc.push(obj.price)
      Time.push(obj.time)
    }

    var element = document.getElementById("currentprice");
    showstr = "Current Price is " + String(obj.price);
    element.innerHTML = showstr;

    updateBarGraph(myChart, btc, Time);
    });
  }, 5000);