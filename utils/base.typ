#let subtitle(content) = [
  #set text(weight: 400)
  #heading(level: 1, content, numbering: none)
]

#let footer(numbered: true, content) = context [
  #set align(center + horizon)
  #set text(10pt)

  #let numbering = []

  #if numbered == true {
    let numbering = counter(page).display(
      "1/1",
      both: true,
    )
  }

  #layout(size => [
    #content
    #h(size.width / 2 - measure(numbering).width / 2 - measure(content).width)
    #counter(page).display(
      "1 / 1",
      both: true,
    )
    #h(1fr)
    #datetime.today().display("[day].[month].[year]")
  ])
]

#let base(dense: false, doc) = [
  #import "@preview/titleize:0.1.1": titlecase

  #set page(
    margin: if dense == false {(top: 2.5cm, left: 3cm)} else {(top: 2.25cm, left: 2.5cm)},
  )
  #set text(12pt, lang: "en", region: "GB")
  #set par(spacing: 1.5em, leading: 1em, justify: true)

  #show title: titlecase
  #show title: set text(if dense == false {37pt} else {22pt})
  #show title: set par(leading: 0.5em, justify: false)
  #show title: set block(below: 1em)

  #show heading: titlecase
  #show heading.where(level: 1): set par(leading: 0.65em)
  #show heading.where(level: 1): set block(
    above: if dense == false {2em} else {1.5em},
    below: if dense == false {1.5em} else {1em},
  )
  #show heading.where(level: 2): set par(leading: 0.65em)
  #show heading.where(level: 2): set block(
    above: if dense == false {2em} else {1.7em},
    below: if dense == false {1.5em} else {1.3em},
  )
  #show heading.where(level: 3): set text(13pt)
  #show heading.where(level: 3): set block(above: 1.5em, below: 1em)

  #set heading(numbering: "1.")

  #show bibliography: set heading(numbering: "1.")

  #set figure(placement: top)
  #show figure.caption: set par(leading: 0.65em)

  #show link: underline

  #doc
]

#let presentation(doc) = [
  #set text(17pt)
  #set par(justify: false)

  #set heading(numbering: none)

  #show heading.where(level: 1): set text(26pt, weight: 400)
  #show heading.where(level: 1): set block(above: 0.8em, below: 0.8em)
  #show heading.where(level: 2): set text(22pt)
  #show heading.where(level: 2): set block(above: 0.8em, below: 0.8em)
  #show heading.where(level: 3): set text(18pt)
  #show heading.where(level: 3): set block(above: 1em, below: 1.5em)

  #set figure(placement: none)
  #show figure.caption: set text(12pt)
  #show footnote.entry: set text(12pt)

  #set columns(gutter: 40pt)

  #doc
]
