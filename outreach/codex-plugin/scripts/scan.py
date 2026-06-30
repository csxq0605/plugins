#!/usr/bin/env python3
"""
Full faculty scan for outreach - batch fetch professor research interests.
Usage: python scan.py --school CUHK --dept CSE --url https://www.cse.cuhk.edu.hk/people/faculty/
"""
import argparse, csv, json, re, sys, time, urllib.request
from pathlib import Path

CONFIG_DIR = Path.home() / '.outreach'
PROFILES_DIR = CONFIG_DIR / 'profiles'
TASK_DIR = Path.cwd() / '.outreach'


def load_profile():
    """Load user profile keywords from profiles/"""
    kws = []
    if PROFILES_DIR.exists():
        for f in PROFILES_DIR.glob('*.md'):
            t = f.read_text('utf-8').lower()
            for kw in ['agent', 'memory', 'embodied', 'llm', 'language model', 'robot',
                        'computer vision', 'multimodal', 'generative',
                        'reinforcement learning', 'deep learning', 'machine learning',
                        'ai for science', 'scientific', 'rag', 'retrieval',
                        'knowledge base', 'world model', 'slam',
                        'natural language', 'nlp', 'graph neural']:
                if kw in t and kw not in kws:
                    kws.append(kw)
    return kws or ['agent', 'memory', 'llm', 'embodied', 'robot',
                   'computer vision', 'deep learning', 'machine learning',
                   'multimodal', 'reinforcement learning']


def get_faculty_slugs(dept_url):
    """Extract all professor slugs from faculty directory page"""
    slugs = []
    req = urllib.request.Request(dept_url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')

    # Method 1: /people/faculty/{slug}/
    slugs.extend(re.findall(r'/people/faculty/([^"\']+)/', html))
    # Method 2: /faculty/{slug}
    slugs.extend(re.findall(r'/faculty/([^"\']+?)(?:/|\?|")', html))
    # Method 3: JSON embedded data (e.g. Ninja Table filterPagination)
    json_m = re.search(r'filter_members[^[]*(\[.*?\])', html, re.DOTALL)
    if json_m:
        try:
            for m in json.loads(json_m.group(1)):
                if 'post_title' in m and 'post_name' in m:
                    slugs.append(m['post_name'])
        except json.JSONDecodeError:
            pass
    return list(set(slugs))


def fetch_prof(slug, base_url):
    """Fetch a single professor page and extract research interests"""
    url = base_url.rstrip('/') + '/' + slug + '/'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='replace')
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)

        title_m = re.search(r'<title>(.*?)(?:\s*[\-–—].*?)?</title>', html)
        name = title_m.group(1).strip() if title_m else slug.replace('-', ' ').title()

        interest_m = re.search(
            r'Research\s+(?:Interests|Areas)[:\s]*(.*?)'
            r'(?:Biography|Education|Teaching|Publications|Awards|Honors|Contact|Email|Office|Links|Top\s+Cited)',
            text, re.IGNORECASE
        )
        interests = interest_m.group(1).strip()[:300] if interest_m else ''
        if not interests:
            idx = text.lower().find('research')
            if idx > 0:
                interests = text[idx:idx + 200].strip()

        email_m = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        email = email_m.group(1) if email_m else ''

        return {
            'name': name, 'slug': slug, 'email': email,
            'interests': interests or '(not found)', 'url': url
        }
    except Exception as e:
        return {
            'name': slug.replace('-', ' ').title(), 'slug': slug,
            'email': '', 'interests': f'ERROR: {str(e)[:100]}', 'url': url
        }


def score_match(interests, profile_kws):
    """Score professor interests against profile keywords (0-10)"""
    il = interests.lower()
    score = 0
    matched = []

    core = ['agent', 'memory', 'embodied', 'llm', 'language model',
            'robot', 'reinforcement learning', 'multiagent']
    for kw in core:
        if kw in il:
            score += 2
            matched.append(kw)

    general = ['deep learning', 'machine learning', 'computer vision',
               'multimodal', 'generative', 'artificial intelligence',
               'knowledge graph', 'data mining', 'natural language']
    for kw in general:
        if kw in il:
            score += 1
            matched.append(kw)

    score += sum(1 for kw in profile_kws if kw in il)
    return min(score, 10), matched


def main():
    parser = argparse.ArgumentParser(description='Full faculty scan for outreach')
    parser.add_argument('--school', required=True)
    parser.add_argument('--dept', required=True)
    parser.add_argument('--url', required=True, help='Faculty directory URL')
    parser.add_argument('--csv', help='User-provided CSV (skip auto-scan)')
    parser.add_argument('--delay', type=float, default=0.3)
    args = parser.parse_args()

    school_dir = TASK_DIR / 'schools' / f'{args.school}_{args.dept}'
    school_dir.mkdir(parents=True, exist_ok=True)

    if args.csv:
        print(f'[SCAN] Using provided CSV: {args.csv}')
        return

    print(f'[SCAN] School: {args.school}, Dept: {args.dept}')
    print(f'[SCAN] URL: {args.url}')

    # Step 1: Get complete faculty list
    print('[SCAN] Step 1: Getting complete faculty list...')
    slugs = get_faculty_slugs(args.url)
    if not slugs:
        print('[ERROR] No professor slugs found. Check URL or provide CSV.')
        return
    print(f'[SCAN]   Found {len(slugs)} slugs')

    # Step 2: Batch fetch professor pages
    print(f'[SCAN] Step 2: Fetching professor pages (delay={args.delay}s)...')
    base = args.url.rstrip('/')
    for suffix in ['/faculty', '/people']:
        if base.endswith(suffix):
            base = base[:-len(suffix)]
            break

    results = []
    for i, slug in enumerate(slugs):
        if (i + 1) % 10 == 0:
            print(f'[SCAN]   Progress: {i+1}/{len(slugs)}')
        results.append(fetch_prof(slug, base))
        time.sleep(args.delay)

    # Step 3: Score matches
    print('[SCAN] Step 3: Scoring matches against user profile...')
    pkw = load_profile()
    for r in results:
        score, matched = score_match(r['interests'], pkw)
        r['match_score'] = score
        r['matched'] = matched
    results.sort(key=lambda x: -x['match_score'])

    # Step 4: Supplement search (for professors outside standard directory)
    print('[SCAN] Step 4: Supplement search...')
    print(f'[SCAN]   NOTE: Some professors may NOT be in the faculty directory!')
    print(f'[SCAN]   Run additional WebSearch for:')
    print(f'[SCAN]     - site:{args.school.lower()}.edu professor research')
    print(f'[SCAN]     - "{args.school}" "{args.dept}" new faculty 2025 2026')
    print(f'[SCAN]     - "{args.school}" "{args.dept}" courtesy adjunct professor')
    print(f'[SCAN]     - (e.g. James Cheng at CUHK uses ~jcheng, not in /people/faculty/)')
    print(f'[SCAN]   If user points out missing professors, add them manually.')

    # Step 5: Save CSV
    csv_p = school_dir / 'professors.csv'
    with open(csv_p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['name', 'school', 'email', 'homepage', 'department',
                     'research_keywords', 'recruiting', 'match_score',
                     'matched_keywords'])
        for r in results:
            w.writerow([
                r['name'], args.school, r['email'], r['url'], args.dept,
                r['interests'][:200], '', r['match_score'],
                ';'.join(r.get('matched', []))
            ])

    # Report
    tiers = {1: 0, 2: 0, 3: 0, 4: 0}
    for r in results:
        s = r['match_score']
        if s >= 8:
            t = 1
        elif s >= 4:
            t = 2
        elif s >= 2:
            t = 3
        else:
            t = 4
        tiers[t] = tiers.get(t, 0) + 1

    print(f'\n[SCAN] Done! Saved to: {csv_p}')
    print(f'[SCAN] Total: {len(results)} professors')
    print(f'[SCAN]   Tier 1 (perfect match):  {tiers[1]}')
    print(f'[SCAN]   Tier 2 (highly relevant): {tiers[2]}')
    print(f'[SCAN]   Tier 3 (somewhat):        {tiers[3]}')
    print(f'[SCAN]   Tier 4 (not relevant):    {tiers[4]}')
    print(f'[SCAN]')
    print(f'[SCAN] ALSO: Run Step 4 supplement searches above!')
    print(f'[SCAN]')
    print(f'[SCAN] Top matches:')
    for r in results[:10]:
        if r['match_score'] >= 3:
            print(f'  [T{r["match_score"]//3+1}] {r["name"]}: '
                  f'score={r["match_score"]} | {r["interests"][:100]}')


if __name__ == '__main__':
    main()
