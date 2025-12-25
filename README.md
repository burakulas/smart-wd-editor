# Smart WD Editor: LM-Powered Wilson-Devinney Input Manager

**Smart WD Editor** is a Python-based utility designed to modernize the workflow of binary star modeling. It acts as an intelligent bridge between the researcher and the strictly formatted **Wilson-Devinney (WD)** DC input files. 

By leveraging the lightweight **Gemma-2-2b-it** open language model via Hugging Face's Cloud Inference, the editor translates natural language commands into surgical, coordinate-accurate updates, preserving the delicate Fortran-style structure required by the WD code.

---

## Prerequisites

* **Hugging Face Account:** This tool uses the `google/gemma-2-2b-it` model. You must have an account and a **Read-Access Token**.
* **Model Access:** Ensure you have accepted the model's terms of use [here](https://huggingface.co/google/gemma-2-2b-it).
* **Cloud-Based:** This version uses the Hugging Face Inference API via the `huggingface_hub` library. **No local model storage (5-10GB) is required**, and it runs on standard hardware without needing a high-end GPU.

## Key Features

* **Natural Language Interaction:** Update parameters using intuitive commands like *"set inclination to 78.5"* or *"T2 is 0.6370"*.
* **Structural Mapping:** Uses a high-fidelity coordinate matrix derived from the **Wilson and Van Hamme (2015)** documentation to ensure zero-error targeting.
* **Scientific Formatting:** Automatically preserves WD-specific double precision notation (e.g., `D+00` instead of `E+00`).
* **Comprehensive Alias System:** Recognizes diverse terminology (e.g., `Omega1` for `POT1`, `Mass Ratio` for `q`).

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/burakulas/smart-wd-editor.git
   cd smart-wd-editor
    ```

2.  **Install Dependencies:**
    ```bash
    pip install huggingface_hub
    ```

3.  **Configure Environment Variable:**
    The script requires a Hugging Face "Read" token for authentication, which can be generated in your [Hugging Face Settings](https://huggingface.co/settings/tokens). This token allows the editor to securely communicate with the Gemma model via the Cloud Inference API.

    **Windows (PowerShell):**
    ```powershell
    $env:HF_TOKEN="hf_your_token_here"
    ```

    **Linux/Mac:**
    ```bash
    export HF_TOKEN="hf_your_token_here"
    ```

---

## Usage

1.  Place the `wd_input.dat` file in the root directory of the project.
2.  Launch the editor:
    ```bash
    python swd_editor.py
    ```
3.  Enter commands at the prompt:
    * `set t1 to 0.7500`
    * `inclination is 76`
    * `q = 0.42`
4.  Type `q` or `exit` to save your changes to `wd_input_new.dat` and quit.

---

## Supported Parameters

The editor currently supports mapping for the following core WD parameters. The underlying mapping logic is designed to be easily extensible. If a specific WD parameter is not listed, it can be added to the internal coordinate matrix in `swd_editor.py`.

---

## Acknowledgments

This project was developed with the technical assistance of [Gemini](https://gemini.google.com/app), AI-based development tool. 

## References

* **Wilson, R. E. and Van Hamme, W. (2015).** [*Computing Binary Star Observables*](https://faculty.fiu.edu/~vanhamme/wdfiles/ebdoc2015-bf.pdf).
* **Wilson, R. E., Devinney, E. J., Van Hamme, W. (2004).** *WD: Wilson-Devinney binary star modeling*. [ASCL:2004.004](https://ascl.net/2004.004).

## License

This project is licensed under the MIT License.
