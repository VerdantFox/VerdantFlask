class BudgetSummary {
  constructor(element) {
    this.element = element
    this.viewTimePeriod = $("#viewTimePeriod")
    this.total = $(element).find(".summary-total")
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
    this.total.removeClass("in-the-red")
    this.total.removeClass("in-the-green")
    if (this.total.text() === "$0") {
      return
    }
    if (this.total.text().charAt(0) === "-") {
      this.total.addClass("in-the-red")
    } else {
      this.total.addClass("in-the-green")
    }
  }

  createBudgetCategories() {
    $(".budget-category").each((i, el) => {
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
    this.viewTimePeriod = $("#viewTimePeriod")
    this.label = $(element).find(".category-label")
    this.total = $(element).find(".category-total")
    this.isPos = $(element).find(".item-pos").first()
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
    this.total.removeClass("in-the-red")
    this.total.removeClass("in-the-green")
    if (this.total.text() === "$0") {
      return
    }
    if (this.isPos.text() === "True") {
      this.total.addClass("in-the-green")
    } else {
      this.total.addClass("in-the-red")
    }
  }

  createBudgetItems() {
    $(this.element)
      .find(".budget-item")
      .each((i, el) => {
        let budgetItem = new BudgetItem(el, this)
        budgetItem.setListeners()
        this.itemsArr.push(budgetItem)
      })
  }
}

class BudgetItem {
  constructor(element, category) {
    this.category = category
    this.viewTimePeriod = $("#viewTimePeriod")
    this.label = $(element).find(".budget-item-label")
    this.input = $(element).find(".input-val")
    this.inputTimePeriod = $(element).find(".input-timeperiod")
    this.total = $(element).find(".item-total")
    this.isPos = $(element).find(".item-pos")
  }

  setItemTotal() {
    let totalVal = Math.round(
      (this.input.val() * this.inputTimePeriod.val()) /
        this.viewTimePeriod.val()
    )
    this.total.text(formatCurrency(totalVal))
    this.setTotalColor()
    this.category.setCategoryTotal()
  }

  setTotalColor() {
    this.total.removeClass("in-the-red")
    this.total.removeClass("in-the-green")
    if (this.total.text() === "$0") {
      return
    }
    if (this.isPos.text() === "True") {
      this.total.addClass("in-the-green")
    } else {
      this.total.addClass("in-the-red")
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
// Helper function
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

// -------------------------------------------------------------------------
// Entry point
// -------------------------------------------------------------------------
let budgetSummary = new BudgetSummary($("#budget-summary"))
budgetSummary.createBudgetCategories()
