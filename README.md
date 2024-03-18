# DAPRECO to MFOTL conversion

## GDPR Articles Conversion

The [WhyEnf Folder](whyenf_files) contains all the automatically converted MFOTL formulæ and the corresponding signatures, compatible with the WhyEnf enforcer.
Our manual effort of brining the automatically generated specifications into enforceable specifications is shown in [WhyEnf manual folder](whyenf_files_manual).

We have already created [HTML sites](html_parsing/html) for the GDPR articles that are formalized in DAPRECO, together with a flat representation of the article's corresponding RIO formula, and the corresponding MFOTL formula.

### Conversion to HTML Pages

To execute the end-to-end conversion of all GDPR articles from DAPRECO to MFOTL to get the associated HTML pages along with the associated laws, compact RIO formulæ, and converted MFOTL formulæ, run:

```bash
python3 src/gdpr_to_html.py
```
### Conversion to MFOTL specifications
To convert GDPR articles from DAPRECO into its corresponding MFTOL formulæ and signatures that are compatible with WhyEn, run:

```bash
python3 src/gdpr_to_whyenf.py
```
