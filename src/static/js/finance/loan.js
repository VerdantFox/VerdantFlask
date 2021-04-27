const graphsCollapse = $("#graphs-collapse-toggle")
const graphsCarrotDown = $("#graphs-caret-down")
const graphsCarrotRight = $("#graphs-caret-right")

const amortizationCollapse = $("#amortization-collapse-toggle")
const amortizationCarrotDown = $("#amortization-caret-down")
const amortizationCarrotRight = $("#amortization-caret-right")

graphsCollapse.click(function () {
  if (graphsCarrotRight.is(":hidden")) {
    graphsCarrotRight.attr("hidden", false)
    graphsCarrotDown.attr("hidden", true)
  } else {
    graphsCarrotRight.attr("hidden", true)
    graphsCarrotDown.attr("hidden", false)
  }
})
amortizationCollapse.click(function () {
  if (amortizationCarrotRight.is(":hidden")) {
    amortizationCarrotRight.attr("hidden", false)
    amortizationCarrotDown.attr("hidden", true)
  } else {
    amortizationCarrotRight.attr("hidden", true)
    amortizationCarrotDown.attr("hidden", false)
  }
})
