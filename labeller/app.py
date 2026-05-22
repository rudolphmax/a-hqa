import csv
from pathlib import Path
from typing import Union, cast

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageOps
from streamlit.delta_generator import DeltaGenerator

from utils import prepare_label_csv, preprocess_image

cols = ["Num", "Filename", "Reader", "Legibility", "Effort", "Layout", "Letter Formation", "Alteration", "Formation Ziv", "Horizontal Alignment", "Vertical Alignment", "Num Lines", "Num Letters"]  # noqa: E501

if not Path("data/validation_set.csv").is_file():
  raise Exception("No validation dataset csv found.")

samples = pd.read_csv("data/validation_set.csv")

if not Path("data/validation_labels.csv").is_file():
  prepare_label_csv(cols)

labels = pd.read_csv("data/validation_labels.csv", sep=",")
start_index = 0
num_documents = samples.shape[0]

if "round" not in st.session_state:
    st.session_state["round"] = 0

if labels.shape[0] > 0:
  if (labels.shape[0] < samples.shape[0]):
    start_index = labels.shape[0]
    st.session_state.round = 0
  else:
    c = labels.loc[np.isnan(labels["Formation Ziv"])]
    if len(c) > 0:
      start_index = c.index[0]
      st.session_state.round = 1
    else:
      st.session_state.round = 3

if "index" not in st.session_state:
    st.session_state["index"] = start_index

if "reader" not in st.session_state:
    st.session_state["reader"] = labels.iloc[start_index-1]["Reader"]

if "rotation" not in st.session_state:
    st.session_state["rotation"] = 0

if "guidelines" not in st.session_state:
    st.session_state["guidelines"] = "None"

def next_doc(values: dict) -> None:
  st.session_state.rotation = 0

  sample = samples.iloc[st.session_state.index]

  labels.loc[st.session_state.index] = [
    sample["Num"],
    sample["Filename"],
    values["reader"],
    values["legibility"],
    values["effort"],
    values["layout"],
    values["letter-formation"],
    values["alteration"],
    values["formation-ziv"],
    values["hor-alignment"],
    values["vert-alignment"],
    values["num-lines"],
    values["num-letters"],
  ]

  labels.to_csv("data/validation_labels.csv", index=False)

  if (st.session_state.index < num_documents-1):
    st.session_state.index += 1
  else:
    st.session_state.index = 0

  st.rerun()

def switch_guidelines() -> None:
  st.session_state.guidelines = st.session_state.guideline_switch

def field(container: DeltaGenerator, name: str) -> DeltaGenerator:
  left, right = container.columns([2, 3])
  left.markdown("###### " + name)

  return right

def question(container: DeltaGenerator, name: str, desc: str, key: str) -> int:
  right = field(container, name)

  return right.slider(desc, 1, 5, 1, key=key)

st.set_page_config(layout="wide")

if st.session_state.round == 3:
  st.header("You're Done!")
  st.text("That's it! All " + str(num_documents) + " documents are labelled. You can now close this window.")
  st.balloons()

else:
  left_column, right_column = st.columns(2, gap="large")

  with left_column:
    sample = samples.iloc[st.session_state.index]

    info = st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center")
    info.text("Doc: " + str(sample["Num"]))
    info.text(str(st.session_state.index + 1) + "/" + str(num_documents))

    rotate_container = info.container(horizontal=True, width="content")

    def rotate_left() -> None:
      st.session_state.rotation += 1

    def rotate_right() -> None:
      st.session_state.rotation -= 1

    rotate_container.button("rotate left", on_click=rotate_left, type="tertiary", icon=":material/rotate_left:")
    rotate_container.button("rotate right", on_click=rotate_right, type="tertiary", icon=":material/rotate_right:", icon_position="right")  # noqa: E501

    img = Image.open(sample["Filename"])
    img = ImageOps.exif_transpose(img)
    img = img.rotate(st.session_state.rotation, expand=False)
    img, img_vert, img_hor = preprocess_image(img)

    if (st.session_state.guidelines == "Horizontal"):
      st.image(image=cast("Image.Image", img_hor))
    elif (st.session_state.guidelines == "Vertical"):
      st.image(image=cast("Image.Image", img_vert))
    else:
      st.image(image=cast("Image.Image", img))

    st.session_state.reader = st.text_input("Reader", labels.iloc[start_index-1]["Reader"], width=100)

  with right_column:
    st.space("medium")

    if (st.session_state.round == 0):
      with st.form("hls_questionnaire", clear_on_submit=True, enter_to_submit=False):
        q = st.container(gap="medium")

        legibility = question(q, "Legibility", "Overall, how legible is the text when first reading?", "legibility")
        effort = question(
          q,
          "Effort",
          "How much effort is required for you to read the document overall?",
          "effort",
        )
        layout = question(
          q,
          "Layout",
          """An overall impression of the layout of writing
          on the page. Well organised handwriting is consistent, with elements
          appropriately positioned in relation to each other (e.g. the position of the margin,
          placement of letters on the baseline, spaces within and between words).""",
          "layout",
        )
        letter_formation = question(
          q,
          "Letter Formation",
          """An overall impression of letter formation. Well formed letters are appropriately shaped,
          contain all necessary elements, neat letter closures and are consistent in size and slope.""",
          "letter-formation",
        )
        alteration = question(
          q,
          "Alteration",
          """An overall impression of the attempts made to rectify letters within words. Includes the
          addition of elements, re-tracing  or re-writing of letters.""",
          "alteration",
        )

        button_container = st.container(horizontal=True, horizontal_alignment="right")

        submitted = button_container.form_submit_button("Next")
        if submitted:
          next_doc({
            "reader": st.session_state.reader,
            "legibility": legibility,
            "effort": effort,
            "layout": layout,
            "letter-formation": letter_formation,
            "alteration": alteration,
            "formation-ziv": np.nan,
            "hor-alignment": np.nan,
            "vert-alignment": np.nan,
            "num-lines": np.nan,
            "num-letters": np.nan,
          })

    elif (st.session_state.round == 1):
      st.write(
        """
        This is the second questionnaire. Familiarize yourself with the letter formation chart below.
        If needed, Use the guideline selector to enable guidelines.
        """,
      )

      with st.expander("Letter Formation Chart", expanded=True):
        st.image("presentations/assets/zivianiEvaluationHandwritingPerformance1984_table2.png")

      st.segmented_control(
          "Guidelines", [ "None", "Horizontal", "Vertical" ],
          default=st.session_state.guidelines,
          selection_mode="single",
          key="guideline_switch",
          on_change=switch_guidelines,
      )

      with st.form("ziv_questionnaire", clear_on_submit=True, enter_to_submit=False):
        q = st.container(gap="medium")

        r = field(q, "Number of Letters")
        num_letters = r.number_input(
          "Count the number of letters in the document (a-z, not including symbols).",
          min_value=0,
          value=1,
        )

        r = field(q, "Formation")
        formation_ziv = r.number_input(
          "Count the number of malformed letters according to the provided chart.",
          min_value=0,
          value=0,
        )

        r = field(q, "Horizontal Alignment")

        with r.expander("Edit"):
          st.caption(
            """
            Enable the vertical guidelines. Count the spaces between all words in terms of space between the provided
            guidelines. For example, two words may be separated by 2, 4, or 8 spaces. Make one entry below for each
            word-gap. Round down.
            """,
          )
          hor_alignment = st.data_editor(
            pd.DataFrame(columns=["Hor Spacing"]),  # pyright: ignore[reportArgumentType]
            column_config={
              "Hor Spacing": st.column_config.NumberColumn(
                step=0.1,
              ),
            },
            num_rows="dynamic",
            hide_index=True,
          )

        r = field(q, "Vertical Alignment")

        with r.expander("Edit"):
          st.caption(
            """
            Enable the horizontal guidelines. Count the amount of deviation from a line in terms of space between
            the provided guidelines. Bottom extenders (e.g. loop of a g) don't count.
            For example, a line may deviate by 2, 1, or 6 spaces. Make one entry below for each line-gap. Round down.
            """,
          )
          vert_alignment = st.data_editor(
            pd.DataFrame(columns=["Vert Spacing"]),  # pyright: ignore[reportArgumentType]
            column_config={
              "Vert Spacing": st.column_config.NumberColumn(
                step=0.1,
              ),
            },
            num_rows="dynamic",
            hide_index=True,
          )

        button_container = st.container(horizontal=True, horizontal_alignment="right")
        submitted = button_container.form_submit_button("Next")

        if submitted:
          next_doc({
            "reader": labels.iloc[st.session_state.index]["Reader"],
            "legibility": labels.iloc[st.session_state.index]["Legibility"],
            "effort": labels.iloc[st.session_state.index]["Effort"],
            "layout": labels.iloc[st.session_state.index]["Layout"],
            "letter-formation": labels.iloc[st.session_state.index]["Letter Formation"],
            "alteration": labels.iloc[st.session_state.index]["Alteration"],
            "formation-ziv": 1 - (formation_ziv / num_letters),
            "hor-alignment": hor_alignment["Hor Spacing"].std() / hor_alignment["Hor Spacing"].mean(),
            "vert-alignment": vert_alignment["Vert Spacing"].std() / vert_alignment["Vert Spacing"].mean(),
            "num-lines": len(vert_alignment["Vert Spacing"]),
            "num-letters": num_letters,
          })
