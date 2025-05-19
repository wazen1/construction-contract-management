frappe.pages["boq-import-export"].on_page_load = (wrapper) => {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "BoQ Import/Export",
    single_column: true,
  })

  // Initialize the page
  frappe.boq_import_export = new BoQImportExport(page)
}

class BoQImportExport {
  constructor(page) {
    this.page = page
    this.wrapper = $(page.body)
    this.setup()
  }

  setup() {
    // Load the page content
    frappe.boq_import_export.page = this

    $(frappe.render_template("boq_import_export", {})).appendTo(this.wrapper)

    this.load_tenders()
    this.bind_events()
  }

  load_tenders() {
    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Project Tender",
        filters: {
          status: ["in", ["Draft", "Published", "Under Review"]],
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
    this.wrapper.find(".btn-download-template").on("click", () => {
      this.download_template()
    })

    this.wrapper.find(".btn-import-boq").on("click", () => {
      this.import_boq()
    })

    this.wrapper.find(".btn-export-boq").on("click", () => {
      this.export_boq()
    })

    this.wrapper.find("#tender-select").on("change", () => {
      this.load_boq_preview()
    })
  }

  download_template() {
    frappe.call({
      method: "construction_contract_management.api.boq_template.get_boq_template",
      callback: (r) => {
        if (r.message) {
          // Create a blob and download
          const blob = new Blob([r.message], { type: "text/csv" })
          const link = document.createElement("a")
          link.href = window.URL.createObjectURL(blob)
          link.download = "boq_template.csv"
          link.click()
        }
      },
    })
  }

  import_boq() {
    const tender_id = this.wrapper.find("#tender-select").val()
    const file_input = this.wrapper.find("#boq-import-file")[0]

    if (!tender_id) {
      frappe.msgprint(__("Please select a tender"))
      return
    }

    if (!file_input.files || !file_input.files.length) {
      frappe.msgprint(__("Please select a CSV file to import"))
      return
    }

    const file = file_input.files[0]
    const reader = new FileReader()

    reader.onload = (e) => {
      const csv_content = e.target.result

      frappe.call({
        method: "construction_contract_management.api.boq_template.import_boq",
        args: {
          tender_id: tender_id,
          csv_content: csv_content,
        },
        callback: (r) => {
          if (r.message && r.message.status === "success") {
            frappe.msgprint(r.message.message)
            this.load_boq_preview()
          } else {
            frappe.msgprint(r.message.message || __("Error importing BoQ"))
          }
        },
      })
    }

    reader.readAsText(file)
  }

  export_boq() {
    const tender_id = this.wrapper.find("#tender-select").val()

    if (!tender_id) {
      frappe.msgprint(__("Please select a tender"))
      return
    }

    frappe.call({
      method: "construction_contract_management.api.boq_template.export_boq",
      args: {
        tender_id: tender_id,
      },
      callback: (r) => {
        if (r.message) {
          // Create a blob and download
          const blob = new Blob([r.message], { type: "text/csv" })
          const link = document.createElement("a")
          link.href = window.URL.createObjectURL(blob)
          link.download = `boq_${tender_id}.csv`
          link.click()
        }
      },
    })
  }

  load_boq_preview() {
    const tender_id = this.wrapper.find("#tender-select").val()

    if (!tender_id) {
      this.wrapper.find(".boq-preview").addClass("hide")
      return
    }

    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Bill of Quantities",
        filters: {
          parent_tender: tender_id,
        },
        fields: ["item_code", "description", "quantity", "uom", "estimated_unit_rate", "total_amount"],
      },
      callback: (r) => {
        const preview_body = this.wrapper.find(".boq-preview-body")
        preview_body.empty()

        if (r.message && r.message.length) {
          r.message.forEach((item) => {
            preview_body.append(`
                            <tr>
                                <td>${item.item_code || ""}</td>
                                <td>${item.description || ""}</td>
                                <td>${item.quantity || 0}</td>
                                <td>${item.uom || ""}</td>
                                <td>${format_currency(item.estimated_unit_rate)}</td>
                                <td>${format_currency(item.total_amount)}</td>
                            </tr>
                        `)
          })

          this.wrapper.find(".boq-preview").removeClass("hide")
        } else {
          preview_body.append(`
                        <tr>
                            <td colspan="6" class="text-center">No BoQ items found for this tender</td>
                        </tr>
                    `)

          this.wrapper.find(".boq-preview").removeClass("hide")
        }
      },
    })
  }
}
