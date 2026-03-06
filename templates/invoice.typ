// French number formatting (e.g. 3 000,00)
#let fr-number(n, decimals: 2) = {
  let integer-part = calc.floor(n)
  let decimal-part = calc.round((n - integer-part) * calc.pow(10, decimals))
  let int-str = str(integer-part)
  // Thousands separator
  let chars = int-str.clusters()
  let len = chars.len()
  let grouped = ""
  for (i, c) in chars.enumerate() {
    if i > 0 and calc.rem(len - i, 3) == 0 { grouped += " " }
    grouped += c
  }
  let dec-str = str(decimal-part)
  while dec-str.len() < decimals { dec-str = "0" + dec-str }
  grouped + "," + dec-str
}


#let invoice(
  // invoice
  invoice_number: "2026F01-042",
  invoice_date: datetime.today().display("[day]/[month]/[year]"),
  // issuer
  issuer_name: "Jane Doe",
  issuer_email: "jane@doe.com",
  issuer_address: "123 Rue de Paris",
  issuer_postal: "75001",
  issuer_city: "Paris",
  issuer_siret: "123 456 789 00010",
  issuer_siren: "123 456 789",
  issuer_vat_number: "FR 12 123 456 789",
  issuer_iban: "FR76 1234 5678 9012 3456 7890 123",
  issuer_bic: "AGRIFRPP123",
  issuer_tax_rate: 0.20,
  // client
  client_name: "Acme Corp",
  client_address: "42 avenue des Champs-Élysées",
  client_postal: "75008",
  client_city: "Paris",
  client_siren: "987 654 321",
  client_vat_number: "FR 98 987 654 321",
  // service
  service_description: "Prestation de services — conseil et accompagnement stratégique",
  service_daily_rate: 600,
  service_days: 20,
) = {
  // ── Calculations ───────────────────────────────────────
  let days = service_days
  let daily-rate = service_daily_rate
  let subtotal = days * daily-rate
  let tax-rate = issuer_tax_rate
  let tax-pct = int(tax-rate * 100)
  let tax = subtotal * tax-rate
  let total = subtotal + tax

  // ── Document configuration ─────────────────────────────
  set document(title: "Facture " + str(invoice_number), author: issuer_name)
  set page(paper: "a4", margin: 1.5cm)
  set text(font: "Helvetica Neue", size: 13pt / 1.5 * 1.3, lang: "fr")
  set par(leading: 0.8em)

  // ── Colors ─────────────────────────────────────────────
  let primary = rgb("#3D5A80")
  let text-dark = rgb("#111827")
  let text-mid = rgb("#374151")
  let text-light = rgb("#4B5563")
  let border-color = rgb("#e0e0e0")
  let bg-light = rgb("#f9f9f9")
  let border-thin = rgb("#ebebeb")

  // ── Header ─────────────────────────────────────────────
  grid(
    columns: (1fr, auto),
    [
      #text(size: 20pt, weight: "bold", tracking: -0.5pt, fill: primary)[#issuer_name]
      #v(1.5em, weak: true)
      #set text(size: 10pt, fill: text-mid)
      #issuer_address \
      #issuer_postal #issuer_city \
      SIRET : #issuer_siret \
      N° TVA : #issuer_vat_number
      #if issuer_email != "" { linebreak() + issuer_email }
    ],
    align(right)[
      #text(size: 8.5pt, weight: 600, tracking: 0.08em, fill: text-light)[
        #upper[Facture]
      ]
      #v(1em, weak: true)
      #text(size: 17pt, weight: "bold", fill: primary)[#invoice_number]
      #v(1em, weak: true)
      #text(size: 10pt, fill: text-mid)[#invoice_date]
    ],
  )

  v(48pt)

  // ── Parties (Issuer / Client) ──────────────────────────
  grid(
    columns: (1fr, 32pt, 1fr),
    grid.cell(
      fill: bg-light,
      inset: (x: 24pt, y: 20pt),
    )[
      #text(size: 8pt, weight: 600, tracking: 0.1em, fill: text-light)[#upper[Émetteur]]
      #v(1em, weak: true)
      #text(size: 11.5pt, weight: "bold", fill: primary)[#issuer_name]
      #v(1pt)
      #set text(size: 10pt, fill: text-mid)
      #issuer_address \
      #issuer_postal #issuer_city \
      SIREN : #issuer_siren \
      N° TVA : #issuer_vat_number
    ],
    [],
    grid.cell(
      fill: bg-light,
      inset: (x: 24pt, y: 20pt),
    )[
      #text(size: 8pt, weight: 600, tracking: 0.1em, fill: text-light)[#upper[Client]]
      #v(1em, weak: true)
      #text(size: 11.5pt, weight: "bold", fill: primary)[#client_name]
      #v(4pt)
      #set text(size: 10pt, fill: text-mid)
      #client_address \
      #client_postal #client_city \
      SIREN : #client_siren \
      N° TVA : #client_vat_number
    ],
  )

  v(25pt)

  // ── Services table ─────────────────────────────────────
  set table(stroke: border-color)

  table(
    columns: (1fr, auto, auto, auto),
    align: (left, right, right, right),
    inset: (x: 14pt, y: 12pt),

    // Headers
    table.header(
      table.cell(fill: primary, text(fill: white, size: 8.5pt, weight: 600, tracking: 0.07em)[#upper[Description]]),
      table.cell(fill: primary, text(fill: white, size: 8.5pt, weight: 600, tracking: 0.07em)[#upper[Qté (jours)]]),
      table.cell(fill: primary, text(fill: white, size: 8.5pt, weight: 600, tracking: 0.07em)[#upper[TJM (€)]]),
      table.cell(fill: primary, text(fill: white, size: 8.5pt, weight: 600, tracking: 0.07em)[#upper[Total HT (€)]]),
    ),

    // Service line item
    [#service_description], [#days], [#fr-number(daily-rate, decimals: 0)], [#fr-number(subtotal)],
  )

  v(25pt)

  // ── Totals ─────────────────────────────────────────────
  align(right)[
    #block(width: 200pt)[
      #grid(
        columns: (auto, 1fr, auto),
        row-gutter: 0pt,

        // Subtotal (excl. tax)
        block(inset: (y: 8pt))[
          #text(weight: 600)[Sous-total HT]
        ],
        block(inset: (y: 8pt))[],
        block(inset: (y: 8pt))[
          #align(right)[#fr-number(subtotal) €]
        ],

        // Separator
        grid.cell(colspan: 3, line(length: 100%, stroke: 0.5pt + border-thin)),

        // VAT
        block(inset: (y: 8pt))[
          #text(weight: 600)[TVA (#tax-pct %)]
        ],
        block(inset: (y: 8pt))[],
        block(inset: (y: 8pt))[
          #fr-number(tax) €
        ],

        // Separator
        grid.cell(colspan: 3, line(length: 100%, stroke: 0.5pt + border-thin)),

        // Total (incl. tax)
        block(inset: (top: 12pt, bottom: 8pt))[
          #text(size: 11.5pt, weight: "bold", fill: primary)[Total TTC]
        ],
        block(inset: (top: 12pt, bottom: 8pt))[],
        block(inset: (top: 12pt, bottom: 8pt))[
          #text(size: 11.5pt, weight: "bold", fill: primary)[#fr-number(total) €]
        ],
      )
    ]
  ]

  v(40pt)

  // ── Footer / Payment terms ─────────────────────────────
  line(length: 100%, stroke: 0.5pt + border-thin)
  v(20pt)

  block[
    #block(
      fill: primary,
      radius: 3pt,
      inset: (x: 8pt, y: 5pt),
    )[
      #text(size: 8pt, weight: "bold", fill: white, tracking: 0.08em)[#upper[Conditions de paiement]]
    ]
    #v(1em, weak: true)
    #set text(size: 8.5pt, fill: text-light)
    #set par(leading: 0.8em)
    #text(weight: "bold", fill: text-dark)[Échéance :] 30 jours à compter de la date de facturation. \
    #text(weight: "bold", fill: text-dark)[Virement bancaire :] IBAN #issuer_iban — SWIFT #issuer_bic \
    #text(weight: "bold", fill: text-dark)[Pénalités de retard :] Tout retard de paiement entraîne des pénalités au taux légal en vigueur, ainsi qu'une indemnité forfaitaire de recouvrement de 40 €.
  ]
}