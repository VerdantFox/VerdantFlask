// -------------------------------------------------------------------------
// Global variables
// -------------------------------------------------------------------------
const budgetItemCreatorHTML = `<div class="row budget-item-creator">
  <div class="col-md">
    <input maxlength="40" class="form-control input-val new-item-name" placeholder="New Item Name">
  </div>
  <div class="col-md">
    <button type="button" class="float-right btn btn-green ml-auto new-item-add-button">Add Item</button>
  </div>
</div>`

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
  budgetForm: "#budget-form",
  categoryCreator: "#category-creator",
  newCategoryName: "#new-category-name",
  newCategoryPos: "#new-cat-pos",
  newCategoryAddButton: "#new-category-add-button",
  newItemCreator: ".budget-item-creator",
  newItemName: ".new-item-name",
  newItemAddButton: ".new-item-add-button",
  catDelBtn: ".cat-del-btn",
  catDelConfirm: ".cat-del-confirm",
  catDelCancel: ".cat-del-cancel",
  itemDelBtn: ".item-del-btn",
  itemDelConfirm: ".item-del-confirm",
  itemDelCancel: ".item-del-cancel",
  catDropdown: ".cat-dropdown",
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
    this.categoryCounter = 0
    this.categoriesArr = []
  }

  setSummaryTotal() {
    let totalVal = 0
    this.categoriesArr.forEach((category) => {
      let categoryTotal = getNumFromCurrency(category.total.text())
      if (category.isPos === "True") {
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

  addBudgetCategories() {
    $(domStrings.budgetCategory).each((i, el) => {
      this.categoryCounter += 1
      const budgetCategory = new BudgetCategory(el, this)
      budgetCategory.addBudgetItems()
      budgetCategory.setCategoryTotal()
      this.categoriesArr.push(budgetCategory)
      budgetCategory.setListeners()
    })
  }

  newCategoryHtmlCreator(category_name) {
    const categoryHTML = `<div id="category-${this.categoryCounter}" class="budget-category">
      <div data-toggle="collapse" data-target="#collapse-${this.categoryCounter}" class="cursor-pointer card-header fs-rem-1-8">
        <div class="row">
          <div class="col-md">
            <span class="dropdown">
              <span class="cat-del-btn" data-toggle="dropdown">
                <i class="far fa-times-circle"></i>
                <i class="fas fa-times-circle"></i>
              </span>
              <div class="dropdown-menu">
                <button type="button" class="dropdown-item cat-del-confirm">Delete</button>
                <button type="button" class="dropdown-item">Cancel</a>
              </div>
            </span>
            <span class="category-label">${category_name}</span>
          </div>
          <div class="col-md"><span class="float-right category-total">$0</span></div>
        </div>
      </div>
      <div id="collapse-${this.categoryCounter}" class="collapse fs-rem-1-4">
        ${budgetItemCreatorHTML}
      </div>
    </div>`
    return $.parseHTML(categoryHTML)
  }

  createNewBudgetCategory() {
    this.categoryCounter += 1
    const isPos = $(domStrings.newCategoryPos).val()
    const categoryName = $(domStrings.newCategoryName).val()
    const lastCategory = this.categoriesArr[this.categoriesArr.length - 1]
      .element
    const newCategory = this.newCategoryHtmlCreator(categoryName)
    $(lastCategory).after(newCategory)
    const budgetCategory = new BudgetCategory(newCategory, this, isPos)
    this.categoriesArr.push(budgetCategory)
    budgetCategory.setListeners()
  }

  deleteBudgetCategory(category) {
    this.categoriesArr = this.categoriesArr.filter((e) => e !== category)
    $(category.element).remove()
  }
}

class BudgetCategory {
  constructor(element, summary, isPos = null) {
    this.element = element
    this.summary = summary
    this.id = $(element).attr("id")
    this.viewTimePeriod = $(domStrings.viewTimePeriod)
    this.label = $(element).find(domStrings.categoryLabel)
    this.total = $(element).find(domStrings.categoryTotal)
    if (isPos) {
      this.isPos = isPos
    } else {
      this.isPos = $(element).find(domStrings.itemPos).first().text()
    }
    this.newItemCreator = $(element).find(domStrings.newItemCreator).first()
    this.newItemName = $(element).find(domStrings.newItemName).first()
    this.newItemAddButton = $(element).find(domStrings.newItemAddButton).first()
    this.catDelConfirm = $(element).find(domStrings.catDelConfirm).first()
    this.catDelCancel = $(element).find(domStrings.catDelCancel).first()
    this.catDropdown = $(element).find(domStrings.catDropdown).first()
    this.budgetItemCounter = 0
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
    if (this.isPos === "True") {
      this.total.addClass(domStrings.green)
    } else {
      this.total.addClass(domStrings.red)
    }
  }

  addBudgetItems() {
    $(this.element)
      .find(domStrings.budgetItem)
      .each((i, el) => {
        this.budgetItemCounter += 1
        const budgetItem = new BudgetItem(el, this)
        budgetItem.setListeners()
        this.itemsArr.push(budgetItem)
        budgetItem.setItemTotal()
      })
  }

  newItemHtmlCreator(itemName) {
    const budgetItemHTML = `<div id="budget-item-${this.budgetItemCounter}" class="row budget-item">
      <div class="col-sm">
        <span class="dropdown">
          <span class="item-del-btn" data-toggle="dropdown">
            <i class="far fa-times-circle"></i>
            <i class="fas fa-times-circle"></i>
          </span>
          <div class="dropdown-menu">
            <button type="button" class="dropdown-item item-del-confirm">Delete</button>
            <button type="button" class="dropdown-item">Cancel</button>
          </div>
        </span>
        <span class="budget-item-label">${itemName}</span>
      </div>
      <div class="col">
        <input class="form-control input-val" inputmode="decimal" type="number" }}">
      </div>
      <div class="col">
        <select class="form-control input-timeperiod">
          <option value="52">Weekly</option>
          <option value="26">Fortnightly</option>
          <option value="24">Bimonthly</option>
          <option selected value="12">Monthly</option>
          <option value="4">Quarterly</option>
          <option value="2">Biannually</option>
          <option value="1">Annually</option>
        </select>
      </div>
      <div class="col text-right">
        <span class="item-total">$0</span>
        <span class="item-pos" hidden>${this.isPos}</span>
      </div>
    </div>`
    return $.parseHTML(budgetItemHTML)
  }

  createNewBudgetItem() {
    this.budgetItemCounter += 1
    const itemName = this.newItemName.val()
    const newItem = this.newItemHtmlCreator(itemName)
    $(this.newItemCreator).before(newItem)
    const budgetItem = new BudgetItem(newItem, this)
    budgetItem.setListeners()
    this.itemsArr.push(budgetItem)
    budgetItem.setItemTotal()
  }

  deleteBudgetItem(item) {
    this.itemsArr = this.itemsArr.filter((e) => e !== item)
    $(item.element).remove()
  }

  setListeners() {
    this.newItemAddButton.click(() => {
      this.createNewBudgetItem()
      this.newItemName.val("")
    })
    this.newItemName.keypress((key) => {
      if (key.which == 13) {
        key.preventDefault()
        this.createNewBudgetItem()
        this.newItemName.val("")
      }
    })
    this.catDelConfirm.click((event) => {
      event.stopPropagation()
      this.catDropdown.removeClass("show")
      this.summary.deleteBudgetCategory(this)
    })
    this.catDelCancel.click((event) => {
      event.stopPropagation()
      this.catDropdown.removeClass("show")
    })
  }
}

class BudgetItem {
  constructor(element, category) {
    this.element = element
    this.category = category
    this.id = $(element).attr("id")
    this.viewTimePeriod = $(domStrings.viewTimePeriod)
    this.label = $(element).find(domStrings.budgetItemLabel)
    this.input = $(element).find(domStrings.budgetItemInput)
    this.inputTimePeriod = $(element).find(domStrings.budgetItemTimeperiod)
    this.total = $(element).find(domStrings.itemTotal)
    this.isPos = $(element).find(domStrings.itemPos).text()
    this.itemDelConfirm = $(element).find(domStrings.itemDelConfirm).first()
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
    console.log(this.isPos)
    if (this.isPos === "True") {
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
    this.itemDelConfirm.click(() => {
      this.category.deleteBudgetItem(this)
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
      if (item.isPos === "True") {
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
  $.post(
    "/finance/budget/stash",
    $(domStrings.budgetForm).serialize(),
    function (data) {
      console.log(`Stashed budget at ${budgetStashTime}.`)
    }
  )
    .done(function () {
      console.log("Success!")
    })
    .fail(function () {
      console.log("Error Stashing budget...")
    })
}

function addEvents(budgetSummary) {
  $(domStrings.newCategoryAddButton).click(() => {
    budgetSummary.createNewBudgetCategory()
    $(domStrings.newCategoryName).val("")
  })
  $(domStrings.newCategoryName).keypress((key) => {
    if (key.which == 13) {
      key.preventDefault()
      budgetSummary.createNewBudgetCategory()
      $(domStrings.newCategoryName).val("")
    }
  })
  $(domStrings.budgetName).change(() => {
    budgetUpdatedTime = new Date()
  })
  $(domStrings.viewTimePeriod).change(() => {
    budgetUpdatedTime = new Date()
  })
}

function setUpBudget() {
  budgetSummary = new BudgetSummary($(domStrings.budgetSummary))
  budgetSummary.addBudgetCategories()
  addEvents(budgetSummary)
  setBudgetJson()
  setInterval(stashBudget, 10000)
}

// -------------------------------------------------------------------------
// Entry point
// -------------------------------------------------------------------------
setUpBudget()
