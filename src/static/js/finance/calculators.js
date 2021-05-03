const graphsCollapse = $("#graphs-collapse-toggle")
const graphsCarrotDown = $("#graphs-caret-down")
const graphsCarrotRight = $("#graphs-caret-right")

const tableCollapse = $("#table-collapse-toggle")
const tableCarrotDown = $("#table-caret-down")
const tableCarrotRight = $("#table-caret-right")

graphsCollapse.click(function () {
  if (graphsCarrotRight.is(":hidden")) {
    graphsCarrotRight.attr("hidden", false)
    graphsCarrotDown.attr("hidden", true)
  } else {
    graphsCarrotRight.attr("hidden", true)
    graphsCarrotDown.attr("hidden", false)
  }
})
tableCollapse.click(function () {
  if (tableCarrotRight.is(":hidden")) {
    tableCarrotRight.attr("hidden", false)
    tableCarrotDown.attr("hidden", true)
  } else {
    tableCarrotRight.attr("hidden", true)
    tableCarrotDown.attr("hidden", false)
  }
})
