#let slide(
  heading: none,
  background: none,
  first: false,
  content
) = context page(
  background: background,
  flipped: true,
  footer: context [
    #if first == false [
      #set align(right + horizon)
      #set text(12pt)

      #counter(page).display(
        "1/1",
        both: true
      )
    ] else []
  ]
)[
  #if heading != none [
    #heading
    #v(15pt)
  ] else []

  #let contentSize = measure(content)

  #let minheight(body) = layout(
    available => {
      let size = measure(body, width: available.width, height: auto)
      let args = if size.height <= available.height { (height: 1fr) }

      block(..args, body)
    }
  )

  #set align(horizon)

  #minheight(content)
]
