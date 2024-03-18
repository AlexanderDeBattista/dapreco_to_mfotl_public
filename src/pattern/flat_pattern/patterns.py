from util.text_parser.text_to_pattern import text_to_pattern 
use_text = "prOnto:DataSubject(w) AND prOnto:PersonalData(z, w) AND prOnto:Controller(y, z) AND prOnto:Processor(x) AND prOnto:nominates(y, x) AND prOnto:PersonalDataProcessing(x, z) AND prOnto:Purpose(epu) AND prOnto:isBasedOn(ep, epu)"
consent_text = "prOnto:DataSubject(w) AND prOnto:PersonalData(z, w) AND prOnto:Controller(y, z) AND prOnto:Processor(x) AND prOnto:nominates(edp, y, x) AND prOnto:PersonalDataProcessing(ep, x, z) AND prOnto:Purpose(epu) AND prOnto:isBasedOn(ep, epu) AND prOnto:Consent(c) AND dapreco:AuthorizedBy(eau, epu, c)"
use = text_to_pattern(use_text, "")
consent = text_to_pattern(consent_text, "")