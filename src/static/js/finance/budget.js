// -------------------------------------------------------------------------
// Global variables
// -------------------------------------------------------------------------
const domStrings = {
  budgetName: "#budget_name",
  viewTimePeriod: "#budget_view_period",
  budgetJson: "#budget_json",
  summaryTotal: ".summary-total",
  red: "in-the-red",
  green: "in-the-green",
  budgetSummary: "#budget-summary",
  budgetCategory: ".budget-category",
  categoryLabel: ".category-label",
  categoryTotal: ".category-total",
  itemPos: ".item-pos",
  itemTotal: ".item-total",
  budgetItem: ".budget-item",
  budgetItemLabel: ".budget-item-label",
  budgetItemInput: ".input-val",
  budgetItemTimeperiod: ".input-timeperiod",
}
let budgetStashTime = new Date()
let budgetUpdatedTime = new Date()
let budgetSummary

// -------------------------------------------------------------------------
// Classes
// -------------------------------------------------------------------------
class BudgetSummary {
  constructor(element) {
    this.element = element
    this.viewTimePeriod = $(domStrings.viewTimePeriod)
    this.total = $(element).find(domStrings.summaryTotal)
    this.categoriesArr = []
  }

  setSummaryTotal() {
    let totalVal = 0
    this.categoriesArr.forEach((category) => {
      let categoryTotal = getNumFromCurrency(category.total.text())
      if (category.isPos.text() === "True") {
        totalVal += categoryTotal
      } else {
        totalVal -= categoryTotal
      }
    })
    this.total.text(formatCurrency(totalVal))
    this.setTotalColor()
  }

  setTotalColor() {
    this.total.removeClass(domStrings.red)
    this.total.removeClass(domStrings.green)
    if (this.total.text() === "$0") {
      return
    }
    if (this.total.text().charAt(0) === "-") {
      this.total.addClass(domStrings.red)
    } else {
      this.total.addClass(domStrings.green)
    }
  }

  createBudgetCategories() {
    $(domStrings.budgetCategory).each((i, el) => {
      let budgetCategory = new BudgetCategory(el, this)
      budgetCategory.createBudgetItems()
      this.categoriesArr.push(budgetCategory)
    })
  }
}

class BudgetCategory {
  constructor(element, summary) {
    this.summary = summary
    this.element = element
    this.viewTimePeriod = $(domStrings.viewTimePeriod)
    this.label = $(element).find(domStrings.categoryLabel)
    this.total = $(element).find(domStrings.categoryTotal)
    this.isPos = $(element).find(domStrings.itemPos).first()
    this.itemsArr = []
  }

  setCategoryTotal() {
    let totalVal = 0
    this.itemsArr.forEach((item) => {
      let itemVal = getNumFromCurrency(item.total.text())
      totalVal += itemVal
    })
    this.total.text(formatCurrency(totalVal))
    this.setTotalColor()
    this.summary.setSummaryTotal()
  }

  setTotalColor() {
    this.total.removeClass(domStrings.red)
    this.total.removeClass(domStrings.green)
    if (this.total.text() === "$0") {
      return
    }
    if (this.isPos.text() === "True") {
      this.total.addClass(domStrings.green)
    } else {
      this.total.addClass(domStrings.red)
    }
  }

  createBudgetItems() {
    $(this.element)
      .find(domStrings.budgetItem)
      .each((i, el) => {
        let budgetItem = new BudgetItem(el, this)
        budgetItem.setListeners()
        this.itemsArr.push(budgetItem)
        budgetItem.setItemTotal()
      })
  }
}

class BudgetItem {
  constructor(element, category) {
    this.category = category
    this.viewTimePeriod = $(domStrings.viewTimePeriod)
    this.label = $(element).find(domStrings.budgetItemLabel)
    this.input = $(element).find(domStrings.budgetItemInput)
    this.inputTimePeriod = $(element).find(domStrings.budgetItemTimeperiod)
    this.total = $(element).find(domStrings.itemTotal)
    this.isPos = $(element).find(domStrings.itemPos)
  }

  setItemTotal() {
    let totalVal = Math.round(
      (this.input.val() * this.inputTimePeriod.val()) /
        this.viewTimePeriod.val()
    )
    this.total.text(formatCurrency(totalVal))
    this.setTotalColor()
    this.category.setCategoryTotal()
    budgetUpdatedTime = new Date()
  }

  setTotalColor() {
    this.total.removeClass(domStrings.red)
    this.total.removeClass(domStrings.green)
    if (this.total.text() === "$0") {
      return
    }
    if (this.isPos.text() === "True") {
      this.total.addClass(domStrings.green)
    } else {
      this.total.addClass(domStrings.red)
    }
  }

  setListeners() {
    this.viewTimePeriod.change(() => {
      this.setItemTotal()
    })
    this.inputTimePeriod.change(() => {
      this.setItemTotal()
    })
    this.input.change(() => {
      this.setItemTotal()
    })
    this.input.keyup(() => {
      this.setItemTotal()
    })
  }
}

// -------------------------------------------------------------------------
// Functions
// -------------------------------------------------------------------------
function formatCurrency(num) {
  let neg = ""
  if (num < 0) {
    neg = "-"
  }
  numFormatted = Math.round(Math.abs(num))
    .toString()
    .replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
  return `${neg}$${numFormatted}`
}

function getNumFromCurrency(currency) {
  return parseInt(currency.replace(/,/g, "").replace(/\$/g, ""), 10)
}

function setBudgetJson() {
  let budgetObj = {}
  budgetSummary.categoriesArr.forEach((category) => {
    budgetObj[category.label.text()] = {}
    category.itemsArr.forEach((item) => {
      let period = parseInt(item.inputTimePeriod.val(), 10)
      let val = parseInt(item.input.val(), 10)
      if (val === NaN) {
        val = null
      }
      let isPos = false
      if (item.isPos.text() === "True") {
        isPos = true
      }
      budgetObj[category.label.text()][item.label.text()] = {
        value: val,
        period: period,
        pos: isPos,
      }
    })
  })
  $(domStrings.budgetJson).val(JSON.stringify(budgetObj))
}

function stashBudget() {
  if (budgetUpdatedTime < budgetStashTime) {
    return
  }
  setBudgetJson()
  budgetStashTime = new Date()
  $.post("/finance/budget/stash", $("#budget-form").serialize(), function (
    data
  ) {
    console.log(`Stashed budget at ${budgetStashTime}.`)
  })
    .done(function () {
      console.log("Success!")
    })
    .fail(function () {
      console.log("Error Stashing budget...")
    })
}

// -------------------------------------------------------------------------
// Entry point
// -------------------------------------------------------------------------
budgetSummary = new BudgetSummary($(domStrings.budgetSummary))
budgetSummary.createBudgetCategories()
$(domStrings.budgetName).change(() => {
  budgetUpdatedTime = new Date()
})
$(domStrings.viewTimePeriod).change(() => {
  budgetUpdatedTime = new Date()
})
setBudgetJson()
setInterval(stashBudget, 15000)
