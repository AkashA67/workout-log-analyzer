from __future__ import annotations
import re
from typing import List, Dict, Any, Optional, Callable, Tuple
from dateutil import parser as dateutil_parser
import sqlite3
import pandas as pd 

date_pattern = re.compile(r"^(\d{1,2}[\-_/]\d{1,2}[\-_/]\d{2,4})\s+(.+)$")

section_pattern = re.compile(r"^\s*([A-Za-z][A-Za-z0-9\s\-\&\(\)]+):?\s*$")

set_pattern = re.compile(
    r"^S(?P<setno>\d+):\s*"
    r"(?:"
        r"(?:(?P<weight>\d+(?:\.\d+)?)\s*(?:kg|kgs)?\s*[\u00D7xX\*]\s*(?P<reps>\d+(?:\.\d+)?(?:\s*\d+(?:\.\d+)?)?)\s*reps?)" # weight x reps
        r"|"
        r"(?:(?P<weight_sec>\d+(?:\.\d+)?)\s*(?:kg|kgs)?\s*[\u00D7xX\*]\s*(?P<time_with_weight>\d+(?:\.\d+)?)\s*sec\b)" # weight + sec
        r"|"
        r"(?:(?P<sec_only>\d+(?:\.\d+)?)\s*sec\b)" # time only
        r"|"
        r"(?:(?P<reps_only>\d+(?:\.\d+)?(?:\s*[\+\-]\s*\d+(?:\.\d+)?)?))\s*reps?\b" # reps only
        r"|"
        r"(?P<catch>.+?)" # catch-all
    r")?"
    r"(?:\s*\((?P<notes>.*?)\))?$",
    re.IGNORECASE
)

set_noprefix_re = re.compile(
    r"(?P<weight>\d+(?:\.\d+)?)\s*(?:kg|kgs)?\s*[×xX\*]\s*(?P<reps>\d+(?:\.\d+)?)",
    re.IGNORECASE
)

clean_prefix = re.compile(r"^\s*[-\u2022]\s*|\s*\d+\.\s*")

exercise_pattern = re.compile(
    r"^(?:[-•]|\d+\.)?\s*([A-Za-z][A-Za-z0-9\s\-\(\)]+[A-Za-z0-9])\s*$"
)


exclude_phrases = {p.lower() for p in [
    'arm circles', 'leg swings', 'band pull-aparts', 'thoracic rotations',
    'stretch', 'cool-down', 'warm-up',
    'superset 1', 'superset 2', 'superset 3',
    'dead hangs', 'v - bar', 'scapular pull-ups',
    'cat-cow stretch', 'total weight', 'total weight including bar'
]}



def normalize_date(datestr: str) -> Optional[str]:
    try:
        dt = dateutil_parser.parse(datestr, dayfirst=True)
        return dt.date().isoformat()
    except Exception:
        return None

def parse_reps_field(raw: str) -> Optional[int]:  # for things like '8', '8+2', '8-10'

    raw = raw.strip()

    if '+' in raw:
        parts = re.split(r"\s*\+\s*", raw)
        try:
            return sum(int(float(p)) for p in parts)
        except:
            return None
    if '-' in raw:
        parts = re.split(r"\s*-\s*", raw)
        try:
            return int(float(parts[0]))
        except:
            return None
    # plain number
    try:
        return int(float(raw))
    except:
        return None

def parse_weight_field(raw: str) -> Optional[float]:
    try:
        return float(raw)
    except:
        # remove stray kg text if exists 
        m = re.search(r"(\d+(?:\.\d+)?)", raw)
        if m: 
            return float(m.group(1))
    return None

def compute_volume(weight: Optional[float], reps: Optional[int]) -> Optional[float]:
    if weight is None or reps is None:
        return None
    return weight * reps

def parse_log_content(raw_log_content: str, *, source_file: Optional[str] = None,
                      ml_label_fn: Optional[Callable[[str], Tuple[str, float]]] = None,
                      save_review_fn: Optional[Callable[[str, float, str, int], None]] = None,
                      conf_threshold: float = 0.60
                      ) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    lines = [ln.rstrip() for ln in raw_log_content.splitlines()]
    lines = [ln for ln in lines if ln and not ln.strip().startswith('#')]

    current_date: Optional[str] = None
    current_program: Optional[str] = None
    current_exercise: Optional[str] = None

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # date line

        m = date_pattern.match(line)
        if m:
            raw_date = m.group(1)
            current_date = normalize_date(raw_date) or raw_date
            current_program = m.group(2).strip()
            current_exercise = None
            continue

        # section/header

        if section_pattern.match(line) or line.strip().startswith('---'):
            current_exercise = None
            continue
        
        # set pattern

        m = set_pattern.match(line)
        if m:
            gd = m.groupdict()
            set_no = int(gd.get('setno'))
            weight = None
            reps = None
            time_sec = None
            iso_load = None
            note = gd.get('notes').strip() if gd.get('notes') else None

            # weight x reps
            if gd.get('weight') and gd.get('reps'):
                weight = parse_weight_field(gd.get('weight'))
                reps = parse_reps_field(gd.get('reps'))
            
            # weight x sec

            elif gd.get('weight_sec') and gd.get('time_with_weight'):
                weight = parse_weight_field(gd.get('weight_sec'))
                try:
                    time_sec = float(gd.get('time_with_weight'))
                except:
                    time_sec = None
                
                # compute isometric load 
                if weight is not None and time_sec is not None:
                    iso_load = weight * time_sec
            
            # sec only
            elif gd.get('sec_only'):
                try:
                    time_sec = float(gd.get('sec_only'))
                except:
                    time_sec = None
            
            # reps only
            elif gd.get('reps_only'):
                reps = parse_reps_field(gd.get('reps_only'))

            #catch-all 
            elif gd.get('catch'):
                catch = gd.get('catch').strip()
                num_match = re.search(r"(\d+)", catch)
                if num_match:
                    reps = int(num_match.group(1))
                else:
                    if not note:
                        note = catch

            # compute volume when weight and reps exist

            volume = compute_volume(weight, reps) if (weight is not None and reps is not None) else None

            has_numeric = (reps is not None or weight is not None or time_sec is not None or iso_load is not None)

            if current_exercise and current_date and (reps is not None or weight is not None or time_sec is not None or iso_load is not None or note):
                rows.append({
                    "date": current_date,
                    "program": current_program,
                    "exercise": current_exercise,
                    "set_no": set_no,
                    "weight_kg": weight,
                    "reps": reps,
                    "time_sec": time_sec,
                    "iso_load": iso_load,
                    "volume": volume,
                    "notes": note
                })
            continue
            
        # exercise name detection 

        m = exercise_pattern.match(line)
        if m:
            raw_name = m.group(1).strip()
            cleaned = clean_prefix.sub("",raw_name).strip()
            # normalize spacing and capitalization
            cleaned_name = re.sub(r"\s{2,}", " ", cleaned)
            if cleaned_name and not cleaned_name.endswith(':'):

                if cleaned_name.startswith('(') and cleaned_name.endswith(')'):
                    continue
                if re.match(r"^\d+(\s*kg)?\s*[×xX]\s*\d+", cleaned_name):
                    continue
                if re.match(r"^\d+(\s*reps?)?$", cleaned_name, re.IGNORECASE):
                    continue
                final_name = cleaned_name

                # Remove rep ranges and notes from exercise names
                final_name = re.sub(
                    r"\s*\(\s*\d{1,3}\s*(?:[-–—]\s*\d{1,3})?\s*(?:reps?|rep)?\s*\)\s*$",
                    "",
                    final_name,
                    flags=re.IGNORECASE
                )
                # Remove trailing unparenthesized ranges like "5-8 reps" or "8-10"
                final_name = re.sub(
                    r"\s*\d{1,3}\s*(?:[-–—]\s*\d{1,3})\s*(?:reps?|rep)?\s*$",
                    "",
                    final_name,
                    flags=re.IGNORECASE
                )
                # Remove notes in exersise name
                final_name = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", "", final_name)

                # remove any leftover rep ranges like "5-8 reps" at end
                final_name = re.sub(
                    r"\s*\d{1,3}\s*(?:[-–—]\s*\d{1,3})\s*(?:reps?|rep)?\s*$",
                    "",
                    final_name,
                    flags=re.IGNORECASE
                )

                # final cleanup
                final_name = re.sub(r"\s{2,}", " ", final_name.strip())

                if final_name:
                    if final_name.lower() in exclude_phrases:
                        current_exercise = None
                    else:
                        current_exercise = final_name
            continue


        # use ML Classifier for ambiguous lines
        if ml_label_fn is not None:
            label, conf = ml_label_fn(line)
            # if low confidence save for manual review
            if conf < conf_threshold and save_review_fn is not None:
                save_review_fn(line, conf, source_file or "<unknown>", i)

            # if ML says this is SET but regex din't match try no-prefix regex:
            if label == "SET":
                m2 = set_noprefix_re.search(line)
                if m2:
                    weight = parse_weight_field(m2.group("weight")) if m2.group("weight") else None
                    reps = parse_reps_field(m2.group("reps")) if m2.group("reps") else None
                    volume = compute_volume(weight, reps) if (weight is not None and reps is not None) else None 
                    if current_exercise and current_date:
                        rows.append({
                            "date": current_date,
                            "program": current_program,
                            "exercise": current_exercise,
                            "set_no": None,
                            "weight_kg": weight,
                            "reps": reps,
                            "time_sec": None,
                            "iso_load": None,
                            "volume": volume,
                            "notes": None
                        })
                    continue
            
            # if ML says its and exercise

            if label == "EXERCISE":
                cleaned = clean_prefix.sub("", line).strip()
                cleaned_name = re.sub(r"\s{2,}"," ", cleaned)
                if cleaned_name and not cleaned_name.endswith(':'):

                    if cleaned_name.startswith('(') and cleaned_name.endswith(')'):
                        continue
                    if re.match(r"^\d+(\s*kg)?\s*[×xX]\s*\d+", cleaned_name):
                        continue
                    if re.match(r"^\d+(\s*reps?)?$", cleaned_name, re.IGNORECASE):
                        continue
                    
                    final_name = cleaned_name

                    # Remove rep ranges and notes from exercise names
                    final_name = re.sub(
                        r"\s*\(\s*\d{1,3}\s*(?:[-–—]\s*\d{1,3})?\s*(?:reps?|rep)?\s*\)\s*$",
                        "",
                        final_name,
                        flags=re.IGNORECASE
                        )
                    # Remove trailing unparenthesized ranges like "5-8 reps" or "8-10"
                    final_name = re.sub(
                        r"\s*\d{1,3}\s*(?:[-–—]\s*\d{1,3})\s*(?:reps?|rep)?\s*$",
                        "",
                        final_name,
                        flags=re.IGNORECASE
                        )
                    # Remove notes in exersise name
                    final_name = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", "", final_name)

                    # remove any leftover rep ranges (rare) like "5-8 reps" at end
                    final_name = re.sub(
                        r"\s*\d{1,3}\s*(?:[-–—]\s*\d{1,3})\s*(?:reps?|rep)?\s*$",
                        "",
                        final_name,
                        flags=re.IGNORECASE
                        )

                    # final cleanup
                    final_name = re.sub(r"\s{2,}", " ", final_name.strip())

                    if final_name:
                        if final_name.lower() in exclude_phrases:
                            current_exercise = None
                        else:
                            current_exercise = final_name
                
                continue

            # if ML says it's NOTE / SECTION / OTHER

            if label == "NOTE":

                if rows:
                    prev = rows[-1]
                    prev["notes"] = (prev.get("notes") or "") + ((" ; " + line) if prev.get("notes") else line)
                continue


            continue

    return rows

