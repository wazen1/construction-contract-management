frappe.pages["bid-comparison-tool"].on_page_load = (wrapper) => {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Bid Comparison Tool",
    single_column: true,
  })

  // Initialize the page
  frappe.bid_comparison_tool = new BidComparisonTool(page)
}

class BidComparisonTool {
  constructor(page) {
    this.page = page
    this.wrapper = $(page.body)
    this.setup()
  }

  setup() {
    // Load the page content
    frappe.bid_comparison_tool.page = this

    $(frappe.render_template("bid_comparison_tool", {})).appendTo(this.wrapper)

    this.load_tenders()
    this.bind_events()
  }

  load_tenders() {
    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Project Tender",
        filters: {
          status: ["in", ["Published", "Under Review", "Awarded"]],
        },
        fields: ["name", "project_title"],
      },
      callback: (r) => {
        const select = this.wrapper.find("#tender-select")
        select.empty()
        select.append('<option value="">Select a Tender</option>')

        r.message.forEach((tender) => {
          select.append(`<option value="${tender.name}">${tender.name} - ${tender.project_title}</option>`)
        })
      },
    })
  }

  bind_events() {
    this.wrapper.find(".btn-generate-comparison").on("click", () => {
      this.generate_comparison()
    })

    this.wrapper.find(".btn-export-comparison").on("click", () => {
      this.export_comparison()
    })
  }

  generate_comparison() {
    const tender_id = this.wrapper.find("#tender-select").val()

    if (!tender_id) {
      frappe.msgprint(__("Please select a tender"))
      return
    }

    frappe.call({
      method: "construction_contract_management.api.bid_comparison.generate_bid_comparison",
      args: {
        tender_id: tender_id,
      },
      callback: (r) => {
        if (r.message && r.message.status === "success") {
          this.render_comparison(r.message.data)
        } else {
          frappe.msgprint(r.message.message || __("No comparison data available"))
        }
      },
    })
  }

  render_comparison(data) {
    // Show the comparison section
    this.wrapper.find(".comparison-results").removeClass("hide")

    // Render bid summary
    const bid_summary = this.wrapper.find(".bid-summary-body")
    bid_summary.empty()

    data.bids.forEach((bid) => {
      bid_summary.append(`
                <tr>
                    <td>${bid.bidder_name}</td>
                    <td>${frappe.format_currency(bid.bid_amount)}</td>
                    <td>${bid.status}</td>
                    <td>${this.calculate_variance(bid.bid_amount, data)}</td>
                </tr>
            `)
    })

    // Render item comparison
    const item_head = this.wrapper.find(".item-comparison-head")
    const item_body = this.wrapper.find(".item-comparison-body")

    item_head.empty()
    item_body.empty()

    // Create header row
    let header_row = "<tr><th>Item Code</th><th>Description</th>"
    data.bids.forEach((bid) => {
      header_row += `<th>${bid.bidder_name}</th>`
    })
    header_row += "</tr>"
    item_head.append(header_row)

    // Create item rows
    data.items.forEach((item) => {
      let row = `<tr><td>${item.item_code}</td><td>${item.description}</td>`

      data.bids.forEach((bid) => {
        const rate = item.bid_rates[bid.bid_id] || "-"
        row += `<td>${rate ? frappe.format_currency(rate) : "-"}</td>`
      })

      row += "</tr>"
      item_body.append(row)
    })

    // Store data for export
    this.comparison_data = data
  }

  calculate_variance(bid_amount, data) {
    // Calculate variance from average or from BoQ estimate
    // This is a placeholder - implement actual calculation
    return "0%"
  }

  export_comparison() {
    if (!this.comparison_data) {
      frappe.msgprint(__("No comparison data to export"))
      return
    }

    // Generate CSV data
    const csv_data = []

    // Add header row
    const header = ["Item Code", "Description"]
    this.comparison_data.bids.forEach((bid) => {
      header.push(bid.bidder_name)
    })
    csv_data.push(header)

    // Add item rows
    this.comparison_data.items.forEach((item) => {
      const row = [item.item_code, item.description]

      this.comparison_data.bids.forEach((bid) => {
        row.push(item.bid_rates[bid.bid_id] || "")
      })

      csv_data.push(row)
    })

    // Convert to CSV string
    let csv_content = "data:text/csv;charset=utf-8,"

    csv_data.forEach((row) => {
      const csv_row = row.join(",")
      csv_content += csv_row + "\r\n"
    })

    // Create download link
    const encoded_uri = encodeURI(csv_content)
    const link = document.createElement("a")
    link.setAttribute("href", encoded_uri)
    link.setAttribute("download", "bid_comparison.csv")
    document.body.appendChild(link)

    // Download the data file
    link.click()
  }
}
