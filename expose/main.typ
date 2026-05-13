#import "../utils/base.typ": base, footer

#import "@preview/gantty:0.5.1": gantt
#import "@preview/titleize:0.1.1": titlecase

#show: base

#set document(
  title: "Automatic handwriting Quality Analysis",
  author: "Maximilian Rudolph"
)

#[
  #set align(center)
  #set text(30pt)

  Exposé
]

#v(2cm)

#[
  #set par(spacing: 1em, leading: 0.65em, justify: false)

  #[
    #set text(21pt)
    #titlecase("Classification Accuracy of Approaches to Automatic handwriting quality analysis and how feature interpretability constrains accuracy")
  ]

  #v(0.25cm)

  Maximilian Rudolph, #datetime.today().display("[day].[month].[year]"), Technische Universität Berlin.\
  Supervised by Prof. Dr. Bettina Berendt.
]

#v(1.5cm)
#outline()

#pagebreak()

#set page(
  footer: footer(numbered: true, [
    Maximilian Rudolph
  ])
)


= Introduction

Handwriting is a key cultural technique of humanity, significant to the development of our modern cultures and their knowledge. However, handwriting is becoming seemingly less practical in a rapidly digitizing world, so typing on keyboards is becoming increasingly popular.
But writing is not just a matter of productivity. Writing by hand is vital for the development of certain motor and intellectual skills in children @ibaibarriagaImpactHandwritingTyping2025, and an important factor in learning for both children and adults @maranoNeuroscienceWritingHandwriting2025 @kieferWritingDigitalAge2016.

A variety of different use cases, such as teaching handwriting, improving posture and reducing risk of injury in adult handwriting, and improving everyday handwriting require a solid means of analysing handwriting quality. Multiple established handwriting quality scales exist that work by manually grading certain aspects of a given document, most prominently @barnettDevelopmentHandwritingLegibility2018a. However, these analyses can be time-consuming and very subjective. So, under certain circumstances, automatic approaches are favourable.

== Defining Quality

In order to meaningfully automate handwriting quality analysis, it is important to know, what defines "good" handwriting. An initial exploratory review of the relevant literature has led to a list of prominent criteria for quality handwriting in @quality-factors. A formal literature review could yield a more conclusive and complete overview, but that is beyond the scope of this thesis. It is also important to note that this list does not yet distinguish between factors for cursive and printed handwriting.

The literature mostly defines handwriting quality by legibility with varying factors attributed to good legibility. Letter size and shape, as well as spacing and line adherence were the most prominent legibility factors in this initial review. Speed is a similarly popular factor, while fluency is mentioned rarely in comparison, most likely due to it being relatively difficult to measure. The time dimension is usually measured separately (as in speed or fluency) and is not present in legibility factors. Most research aims to develop measures that are fast and easy to use, which makes them usable for non-experts and experts alike.

#figure(
  [
    #set text(10pt)
    #set par(leading: 0.5em)

    #show table.cell.where(y: 0): strong
    #show table.cell.where(y: 0): set text(11pt)

    #table(
      inset: 5.5pt,
      align: left + horizon,
      columns: 4,
      table.header(
        table.cell(colspan: 2)[Factor], [Description], [Prominent Sources]
      ),

      table.cell(rowspan: 11)[*Legibility  *], [Global Legibility], [Whether the document is legible on the first read.], [@barnettDevelopmentHandwritingLegibility2018a],

      [Letter Recognizability], [], [@reismanDevelopmentReliabilityResearch1993],

      [Size], [Uniformity and adequacy of letter and sentence size.], [@johnsonMeasuringQualityHandwriting1916 @zivianiEvaluationHandwritingPerformance1984 @reismanDevelopmentReliabilityResearch1993 @fitjarAssessingHandwritingMethod2024 @stefanssonFormativeEvaluationHandwriting2003a],

      [Letter Shape], [Whether letters are normatively well-formed.], [@zivianiEvaluationHandwritingPerformance1984 @reismanDevelopmentReliabilityResearch1993 @fitjarAssessingHandwritingMethod2024 @stefanssonFormativeEvaluationHandwriting2003a],

      [Letters and word spacing], [Uniformity of letter and word spacing.], [@johnsonMeasuringQualityHandwriting1916 @zivianiEvaluationHandwritingPerformance1984 @reismanDevelopmentReliabilityResearch1993 @stefanssonFormativeEvaluationHandwriting2003a],

      [Line adherence], [Uniformity of letter placement within lines of text.], [@johnsonMeasuringQualityHandwriting1916 @zivianiEvaluationHandwritingPerformance1984 @fitjarAssessingHandwritingMethod2024 @stefanssonFormativeEvaluationHandwriting2003a],

      [Layout], [Uniformity of document margins.], [@barnettDevelopmentHandwritingLegibility2018a],

      [Effort to read], [How easy a document feels to read.], [@barnettDevelopmentHandwritingLegibility2018a],

      [Alterations], [Amount of alterations such as strikeouts, re-tracing of letters, etc.], [@barnettDevelopmentHandwritingLegibility2018a],

      [Colour of line], [], [@johnsonMeasuringQualityHandwriting1916],

      [Slant], [Uniformity and angle of slant.], [@johnsonMeasuringQualityHandwriting1916],

      [*Speed*], [], [Time to write a reference text.], [@zivianiEvaluationHandwritingPerformance1984 @stefanssonFormativeEvaluationHandwriting2003a @fitjarAssessingHandwritingMethod2024 @peverlyImportanceHandwritingSpeed2006],

      [*Fluency*], [], [Changes in speed over time.], [@fitjarAssessingHandwritingMethod2024],
    )
  ],
  caption: [Prominent factors impacting handwriting quality.]
)<quality-factors>

== Problems of current approaches

Multiple methods for automatic handwriting quality analysis exist. Many work by extracting certain metrics, so-called _features_, from a handwritten document, which then form a score. Machine learning and regression are also often used for prediction. Most approaches fall short in three key aspects.

+ The selection of features to extract from a given document is inconsistent and often not clearly motivated.
+ Ground truth is acquired very differently, making the comparison of approaches difficult.
+ Almost all approaches (also) rely on non-interpretability in their design or in their features #footnote[
  A feature or method is interpretable if its value is meaningful to a human without further processing.
  Evenness of line spacing is interpretable, for example. A highly abstract metric computed over an entire document or an AI model however, are not considered interpretable.
], but the role non-interpretability plays in achieving a certain performance is not critically examined.

Therefore, it is unclear which features and design choices actually matter, what impact they have and how specific they are to the dataset(s) used for evaluation and training.

== Research Question

The proposed thesis will examine the different approaches for automatic handwriting quality analysis to identify the influence of their features and overall design on analytical performance. Since feature interpretability makes scores easier to work with and inherently meaningful to humans, an emphasis will lie on understanding the relationship between performance and human interpretability. The thesis will be guided by the following (preliminary) research question.

#box(inset: (left: 30pt))[
  #set align(center)

  _Which approaches to automatic handwriting quality analysis classify most accurately, and does feature interpretability constrain accuracy?_
]

The research question will be answered through practical evaluation of the identified approaches and their features as well as a (prototype) scoring mechanism, which will combine the most successful features into one score (#ref(<method>)).

== Focus

Focus will lie on everyday adult handwriting, not on documents produced in early learning stages, by children for example, and not on purely aesthetic works, such as calligraphy. Languages with non-latin alphabets will not be examined, but the research aims to be easily extensible to different languages. Any emerging orientation will be mostly determined by the data used (see #ref(<data>)).

The pursued scoring mechanism itself will not be comprehensively evaluated within the proposed thesis and is meant solely as a basis for further research.


= Method<method>

The space of possible approaches to examine is broad and the (reproducible) implementation of all of them is not feasible. This rules out the possibility of computing an aggregate score of all selected approaches to compare against.
Instead, the goal is to identify categories of approaches (approximately 3-4) and select one representative each for implementation and evaluation.

Once ground truth data is available (see #ref(<data>) for details), the selected category-representatives will be implemented and then evaluated against a predefined test-portion of the dataset.

After evaluation, a selection of the most successful features should form the previously mentioned (prototype) framework.


= Literature Overview

The following sections will briefly detail the currently selected literature and give reasons for their inclusion as well as explain the means of data acquisition.

== Existing HQA Approaches

The approaches of @majumdarVisualAestheticAnalysis2016 @adakLegibilityAestheticAnalysis2017 @kuleshHandwritingQualityEvaluation2001, and @koushikHQA2LFShandwritingQualityAssessment2026 each use various interpretable and non-interpretable features which are all very different in design. In @bouletreauSyntheticParametersHandwriting1997 _fractal geometry_ is used for legibility assessment which will most likely be non-interpretable, but may provide a solid point for comparison, similar to the gradient, binary, and texture features described in @majumdarVisualAestheticAnalysis2016.\
This limited initial selection is relatively representative but will be supplemented with adjacent works to form a more comprehensive overview of the field.

== Data<data>

The data (a set of handwritten documents) should be broad in terms of styles of handwriting and quality. Currently, data from @ICDAR2024HWD @Lee2021, and @ResearchGroupComputer is considered for usage, which would total around $2000$ individual samples. At the time of writing, multiple inquiries for additional data are pending.

Many approaches will require training of some form of AI model, which drastically increases the size requirements for the dataset and requires the data to be labelled. Labelling will be performed along the criteria detailed in @quality-factors, following a standardized approach that most broadly reflects all relevant factors. The methods from @zivianiEvaluationHandwritingPerformance1984 or @stefanssonFormativeEvaluationHandwriting2003a possibly together with @barnettDevelopmentHandwritingLegibility2018a are contenders. Because the datasets only contain images, fluency and speed can not be evaluated.

Fully manual labelling is not feasible due to time constraints, so the following two possibilities for labelling are currently considered.

+ Acquiring labels by aggregating results of existing open-source implementations, such as @dAdityad1Hwa2023 @adityaNithinadityaHandwritinganalysistool2023 @S5TeamWorkspaceHandwritingQualityAssessor2025, and @tharunnTharunn25Handwritingqualityanalysis2023.
+ Using multiple existing LLMs or similar machine learning models as automatic labellers.

In both cases, the automatically generated labels are verified against manually acquired labels on a limited dataset (50–100 samples) before labelling the full set.


= Proposed Outline

@prelim-outline shows the preliminary outline for the proposed thesis. Section 1 is used to motivate this research. In section 2, the current state of research is detailed in addition to an overview of the approaches from literature and their categorization. Section 3 will detail the process (and results) of data acquisition, details of implementation and explain interpretability. In sections 4.1 and 4.2, the implementation and subsequent evaluation are discussed. Sections 4.3 and 4.4 will approach interpretability along the previous evaluation and detail, if and how non-interpretable features are beneficial (or needed) in addition to interpretable features for achieving good performance. Section 4.5 will describe the derived scoring mechanism. Results are discussed in section 5.

#figure(
  [
    #set align(left)
    #set text(10pt)
    #set enum(numbering: (..n) => n.pos().map(str).join(".") + ".", full: true)
    #show enum: titlecase

    + Introduction
      + The Significance of Handwriting in the age of Digital Writing
      + Applications and Use Cases of Handwriting Quality Analysis
    + Status Quo and related Work
      + Manual Methods
      + Current and Past Automatic Approaches
      + Method Overview and Categorisation
    + Method
      + Data Acquisition
      + Implementation Details
      + Feature Interpretability
    + Results
      + Implementation
      + Evaluation
      + Approaching Interpretability
        + Feature Evaluation
        + Benefits
        + Shortcomings
     	+ Supplementing with Non-Interpretable Features
     	+ Consolidated Scoring Mechanism
        + Method and Feature Selection
        + Performance
 	+ Discussion
  ],
  caption: [Preliminary Outline]
)<prelim-outline>


#set page(flipped: true)
= Target Timeline

#set align(horizon)
#figure(
  gantt(yaml("timeline_gantt.yaml")),
  caption: [Proposed Research Timeline],
  placement: none,
)

#set align(top)
#set page(flipped: false)

#pagebreak()

#bibliography("/refs.bib", title: "Bibliography (Preliminary)")
