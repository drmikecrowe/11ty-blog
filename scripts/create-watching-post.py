#!/usr/bin/env python3
"""
Create a Hugo 'watching' post from IMDB data.

Usage:
    python scripts/create-watching-post.py "The Matrix"
    python scripts/create-watching-post.py "Breaking Bad" --currently-watching
    python scripts/create-watching-post.py "Gladiator II" --highly --no-draft
    python scripts/create-watching-post.py "Severance" --date 2025-12
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)

try:
    from io import BytesIO

    from PIL import Image
except ImportError:
    print("Error: pillow not installed. Run: pip install pillow")
    sys.exit(1)

# Thumbnail settings
POSTER_MAX_WIDTH = 400
POSTER_QUALITY = 85


def slugify(title: str) -> str:
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def search_imdb(query: str, limit: int = 3) -> list:
    """Search IMDB using suggestion API and return results."""
    # Use IMDB's suggestion API which is more reliable than scraping
    query_encoded = query.lower().replace(" ", "_")
    first_char = query_encoded[0] if query_encoded else "a"
    url = f"https://v3.sg.media-imdb.com/suggestion/{first_char}/{query_encoded}.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error searching IMDB: {e}")
        return []

    results = []
    for item in data.get("d", []):
        # Skip non-title entries (like people)
        if not item.get("id", "").startswith("tt"):
            continue

        qid = item.get("qid", "")
        # Map qid to kind
        kind_map = {
            "movie": "movie",
            "feature": "movie",
            "tvSeries": "tv series",
            "tvMiniSeries": "tv mini series",
            "video": "video",
            "tvMovie": "tv movie",
            "short": "short",
        }
        kind = kind_map.get(qid, qid)

        # Only include movies and TV series
        if kind not in ("movie", "tv series", "tv mini series"):
            continue

        results.append(
            {
                "imdb_id": item.get("id", "").replace("tt", ""),
                "title": item.get("l", "Unknown"),
                "year": item.get("y"),
                "kind": kind,
                "image_url": item.get("i", {}).get("imageUrl"),
                "stars": item.get("s", ""),  # Actors from search result
            }
        )

    return results[:limit]


def fetch_plot(imdb_id: str) -> str:
    """Fetch plot summary for a single title using IMDB GraphQL API."""
    url = "https://graphql.imdb.com/"
    # graphql.imdb.com 403s without a client-name header — verified 2026-08-26
    headers = {
        "content-type": "application/json",
        "x-imdb-client-name": "imdb-web-next",
    }

    query = """
    query GetPlot($id: ID!) {
      title(id: $id) {
        plot { plotText { plainText } }
      }
    }
    """

    full_id = imdb_id if imdb_id.startswith("tt") else f"tt{imdb_id}"
    payload = {"query": query, "variables": {"id": full_id}}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        plot = data.get("data", {}).get("title", {}).get("plot", {}).get("plotText", {}).get("plainText", "")
        if plot:
            # Truncate to ~80 chars for display
            if len(plot) > 80:
                plot = plot[:77] + "..."
            return plot
    except Exception:
        pass
    return ""


def enrich_results_with_plots(results: list) -> list:
    """Fetch plot summaries for all search results."""
    print("Fetching descriptions", end="", flush=True)
    for item in results:
        plot = fetch_plot(item["imdb_id"])
        item["plot"] = plot
        print(".", end="", flush=True)
    print(" done.")
    return results


def display_results(results: list) -> None:
    """Display search results for user selection."""
    print("\nSearch results:")
    print("-" * 80)
    for i, item in enumerate(results, 1):
        kind = item.get("kind", "unknown")
        year = item.get("year", "????")
        title = item.get("title", "Unknown")
        plot = item.get("plot", "")
        print(f"  {i}. {title} ({year}) [{kind}]")
        if plot:
            print(f"      {plot}")
    print("-" * 80)
    print("  0. Cancel")
    print("-" * 80)


def get_user_selection(results: list) -> int:
    """Get user's selection from results. Returns -1 for cancel."""
    while True:
        try:
            choice = input(f"Select (1-{len(results)}, 0 to cancel): ").strip()
            if choice == "0":
                return -1
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return idx
            print(f"Please enter a number between 0 and {len(results)}")
        except ValueError:
            print("Invalid input. Enter a number.")


def fetch_full_metadata(imdb_id: str) -> dict:
    """Fetch complete metadata for a movie/show using IMDB GraphQL API."""
    url = "https://graphql.imdb.com/"
    # graphql.imdb.com 403s without a client-name header — verified 2026-08-26
    headers = {
        "content-type": "application/json",
        "x-imdb-client-name": "imdb-web-next",
    }

    query = """
    query GetTitle($id: ID!) {
      title(id: $id) {
        titleText { text }
        releaseYear { year }
        ratingsSummary { aggregateRating voteCount }
        genres { genres { text } }
        titleType { id text }
        principalCredits {
          category { id text }
          credits { name { nameText { text } } }
        }
        plot { plotText { plainText } }
        primaryImage { url }
      }
    }
    """

    # Ensure ID has tt prefix
    full_id = imdb_id if imdb_id.startswith("tt") else f"tt{imdb_id}"

    payload = {"query": query, "variables": {"id": full_id}}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        title_data = data.get("data", {}).get("title", {})

        # Parse into a format compatible with the rest of the script
        result = {
            "movieID": imdb_id.replace("tt", ""),
            "title": title_data.get("titleText", {}).get("text", "Unknown"),
            "year": title_data.get("releaseYear", {}).get("year"),
            "kind": title_data.get("titleType", {}).get("id", "movie"),
            "rating": title_data.get("ratingsSummary", {}).get("aggregateRating"),
            "genres": [g.get("text") for g in title_data.get("genres", {}).get("genres", [])],
            "plot": [title_data.get("plot", {}).get("plotText", {}).get("plainText", "")]
            if title_data.get("plot")
            else [],
            "cover url": title_data.get("primaryImage", {}).get("url"),
        }

        # Parse credits (cast, directors, creators)
        for credit_group in title_data.get("principalCredits", []):
            category_id = credit_group.get("category", {}).get("id", "")
            category_text = credit_group.get("category", {}).get("text", "")
            names = [c.get("name", {}).get("nameText", {}).get("text", "") for c in credit_group.get("credits", [])]

            if category_id == "director" or category_text == "Directors":
                result["directors"] = names
            elif category_id == "creator" or category_text == "Creators":
                result["creators"] = names
            elif category_id in ("actor", "actress") or category_text == "Stars":
                result["cast"] = names
            elif category_id == "writer" or category_text == "Writers":
                result["writers"] = names

        return result

    except Exception as e:
        print(f"Error fetching metadata from IMDB API: {e}")
        # Return minimal data
        return {"movieID": imdb_id.replace("tt", ""), "title": "Unknown"}


def download_poster(cover_url: str, dest_path: Path) -> bool:
    """Download poster image and resize to thumbnail."""
    if not cover_url:
        return False

    try:
        # Try to get a higher resolution version by modifying the URL
        # IMDB URLs often have resolution info that can be removed
        # e.g., ...@._V1_UX182_CR0,0,182,268_.jpg -> ...@._V1_.jpg
        full_url = re.sub(r"@\._V1_.*\.jpg", "@._V1_.jpg", cover_url)
        if full_url == cover_url:
            # Try another pattern
            full_url = re.sub(r"\._V1_.*\.jpg", "._V1_.jpg", cover_url)

        print("Downloading poster...")
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()

        # Open image and resize
        img = Image.open(BytesIO(response.content))

        # Resize if wider than max width, maintaining aspect ratio
        if img.width > POSTER_MAX_WIDTH:
            ratio = POSTER_MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((POSTER_MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

        # Convert to RGB if necessary (for JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Save as optimized JPEG
        img.save(dest_path, "JPEG", quality=POSTER_QUALITY, optimize=True)
        print(f"Saved poster ({img.width}x{img.height}) to {dest_path}")
        return True
    except Exception as e:
        print(f"Warning: Failed to download poster: {e}")
        return False


def parse_existing_post(file_path: Path) -> dict:
    """Parse existing post to extract tags, rank, and 'Our Thoughts' content."""
    result = {"tags": [], "thoughts": "", "rank": None}

    if not file_path.exists():
        return result

    content = file_path.read_text()

    # Extract frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]

            # Extract tags from frontmatter
            in_tags = False
            for line in frontmatter.split("\n"):
                if line.strip().startswith("tags:"):
                    in_tags = True
                    continue
                if in_tags:
                    if line.strip().startswith("- "):
                        tag = line.strip()[2:].strip()
                        result["tags"].append(tag)
                    elif line.strip() and not line.startswith(" "):
                        in_tags = False
                # Extract rank
                if line.strip().startswith("rank:"):
                    rank_val = line.split(":", 1)[1].strip()
                    if rank_val:
                        try:
                            result["rank"] = int(rank_val)
                        except ValueError:
                            pass

            # Extract "Our Thoughts" section
            if "## Our Thoughts" in body:
                thoughts_section = body.split("## Our Thoughts", 1)[1]
                # Stop at next section if there is one
                if "\n## " in thoughts_section:
                    thoughts_section = thoughts_section.split("\n## ", 1)[0]
                result["thoughts"] = thoughts_section.strip()

    return result


def generate_post(
    item: dict,
    search_result: dict,
    output_dir: Path,
    draft: bool,
    currently_watching: bool,
    highly_recommended: bool,
    post_date: str,
    existing_data: dict = None,
    new_rank: int = None,
) -> Path:
    """Generate Hugo post content and write to file."""
    today = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().strftime("%Y")

    title = item.get("title", "Unknown")
    year = item.get("year", "")
    plot = ""
    if item.get("plot"):
        plots = item.get("plot")
        if isinstance(plots, list) and plots:
            plot = plots[0]
            # Strip author attribution if present
            if "::" in plot:
                plot = plot.split("::")[0].strip()

    rating = item.get("rating", "")
    genres = item.get("genres", [])
    imdb_id = f"tt{item.get('movieID', '')}"

    # Extract cast and director/creator
    cast = item.get("cast", [])
    if cast:
        actors = ", ".join(str(p) for p in cast[:3])
    else:
        actors = search_result.get("stars", "") or "Unknown"

    # Use directors for movies, creators for TV
    directors = item.get("directors", []) or item.get("creators", [])
    director = ", ".join(str(p) for p in directors[:2]) if directors else "Unknown"

    # Extract writers
    writers = item.get("writers", [])
    writer = ", ".join(str(p) for p in writers[:3]) if writers else None

    # Build tags - preserve existing tags if updating
    if existing_data and existing_data.get("tags"):
        tags = existing_data["tags"]
    else:
        tags = [current_year]
        if currently_watching:
            tags.append("currently-watching")
        if highly_recommended:
            tags.append("highly-recommended")

    # Use existing rank if updating, or new_rank if provided
    rank = None
    if existing_data and existing_data.get("rank"):
        rank = existing_data["rank"]
    elif new_rank:
        rank = new_rank

    # Format genres for YAML
    genres_yaml = ", ".join(f'"{g}"' for g in genres) if genres else ""

    # Build frontmatter
    tags_yaml = "\n".join(f"  - {tag}" for tag in tags)
    rank_line = f"\nrank: {rank}" if rank else ""

    featured_image = (
        "images/hero.jpg" if (output_dir / "images" / "hero.jpg").exists() else ""
    )

    frontmatter = f"""---
title: "{title}"
description: "Our thoughts on {title}"
date: {post_date}
draft: {str(draft).lower()}
tags:
{tags_yaml}{rank_line}
author: Mike Crowe
show_reading_time: true
featured_image: "{featured_image}"
imdb_id: "{imdb_id}"
imdb_rating: {rating if rating else '""'}
genres: [{genres_yaml}]
year: {year if year else '""'}
---"""

    # Build content body
    summary = plot if plot else "*No plot summary available.*"
    imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    rating_str = f"[{rating}/10]({imdb_url})" if rating else f"[N/A]({imdb_url})"

    # Build IMDB section with optional writer line
    imdb_lines = [
        f"- **Actors:** {actors}",
        f"- **Director:** {director}",
    ]
    if writer:
        imdb_lines.append(f"- **Writers:** {writer}")
    imdb_lines.extend([
        f"- **Year:** {year if year else 'Unknown'}",
        f"- **IMDB Rating:** {rating_str}",
    ])
    imdb_section = "\n".join(imdb_lines)

    # Preserve existing thoughts if updating
    thoughts = ""
    if existing_data and existing_data.get("thoughts"):
        thoughts = existing_data["thoughts"]

    content = f"""{frontmatter}

# {title}

## Our Thoughts

{thoughts}

## IMDB Summary

{summary}

## IMDB

{imdb_section}
"""

    index_path = output_dir / "index.md"
    index_path.write_text(content)
    return index_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a Hugo 'watching' post from IMDB data"
    )
    parser.add_argument("query", help="Title to search for on IMDB")
    parser.add_argument(
        "--draft/--no-draft",
        dest="draft",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Set draft status (default: draft)",
    )
    parser.add_argument(
        "--currently-watching",
        action="store_true",
        help="Add 'currently-watching' tag",
    )
    parser.add_argument(
        "--highly-recommended",
        "--highly",
        dest="highly_recommended",
        action="store_true",
        help="Add 'highly-recommended' tag",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite if post already exists",
    )
    parser.add_argument(
        "--rank",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Rank for recommended items (1=top, 5=good)",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Post date in YYYY-MM format (default: current month)",
    )
    parser.add_argument(
        "--tv",
        dest="media_type",
        action="store_const",
        const="tv",
        help="Force creation as TV show",
    )
    parser.add_argument(
        "--movie",
        dest="media_type",
        action="store_const",
        const="movie",
        help="Force creation as movie",
    )
    parser.add_argument(
        "--entries",
        type=int,
        default=3,
        help="Number of search results to return (default: 3). Use 1 to skip selection prompt.",
    )

    args = parser.parse_args()

    # Find content directory
    script_dir = Path(__file__).parent
    content_dir = script_dir.parent / "content" / "watching"

    if not content_dir.exists():
        print(f"Error: Content directory not found: {content_dir}")
        sys.exit(1)

    # Search IMDB
    print(f"Searching IMDB for '{args.query}'...")
    results = search_imdb(args.query, args.entries)

    if not results:
        print("No results found.")
        sys.exit(1)

    # Fetch plot summaries for display
    if args.entries == 1:
        # Skip prompt for single entry
        selected = results[0]
        print(f"Auto-selected: {selected['title']} ({selected.get('year', '????')})")
    else:
        enrich_results_with_plots(results)
        display_results(results)
        selection_idx = get_user_selection(results)
        if selection_idx == -1:
            print("Cancelled.")
            sys.exit(0)
        selected = results[selection_idx]

    print(f"\nFetching full metadata for '{selected['title']}'...")
    item = fetch_full_metadata(selected["imdb_id"])

    # Determine output path based on kind or explicit flag
    if args.media_type == "tv":
        type_dir = content_dir / "tv"
    elif args.media_type == "movie":
        type_dir = content_dir / "movies"
    else:
        kind = item.get("kind", "movie").lower()
        # Handle both cinemagoer format ("tv series") and GraphQL format ("tvSeries")
        if kind in ("tv series", "tv mini series", "tvseries", "tvminiseries", "tvmovie"):
            type_dir = content_dir / "tv"
        else:
            type_dir = content_dir / "movies"

    slug = slugify(item.get("title", "unknown"))

    # Check if post already exists anywhere (search by slug)
    existing_data = None
    existing_dir = None
    for search_dir in [content_dir / "tv", content_dir / "movies"]:
        for date_dir in search_dir.glob("*"):
            if date_dir.is_dir():
                candidate = date_dir / slug
                if candidate.exists() and (candidate / "index.md").exists():
                    existing_dir = candidate
                    break
        if existing_dir:
            break

    if existing_dir:
        if not args.force:
            print(f"Error: Post already exists at {existing_dir}")
            print("Use --force to update (preserves tags and 'Our Thoughts').")
            sys.exit(1)
        # Use existing location and parse existing data
        output_dir = existing_dir
        index_path = output_dir / "index.md"
        print(f"Updating existing post at {output_dir} (preserving tags and 'Our Thoughts')...")
        existing_data = parse_existing_post(index_path)
        # Get date from existing frontmatter
        post_date = None
        content = index_path.read_text()
        for line in content.split("\n"):
            if line.startswith("date:"):
                post_date = line.split(":", 1)[1].strip()
                break
        if not post_date:
            post_date = datetime.now().strftime("%Y-%m-%d")
    else:
        # Create new post
        if args.date and len(args.date) == 7:
            post_date = f"{args.date}-01"
        else:
            post_date = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
        # Folder is always grouped by month (YYYY-MM), regardless of whether
        # --date was given as a full date or just a month.
        current_month = post_date[:7]
        output_dir = type_dir / current_month / slug

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download poster - try cinemagoer URL first, fall back to search result URL
    cover_url = (
        item.get("cover url")
        or item.get("full-size cover url")
        or selected.get("image_url")
    )
    if cover_url:
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        download_poster(cover_url, images_dir / "hero.jpg")
    else:
        print("Warning: No poster available for this title.")

    # Generate post
    post_path = generate_post(
        item,
        selected,
        output_dir,
        args.draft,
        args.currently_watching,
        args.highly_recommended,
        post_date,
        existing_data,
        args.rank,
    )

    action = "Updated" if existing_data else "Created"
    print(f"\n{action} post: {post_path}")
    print(f"Run 'hugo server -D' to preview.")


if __name__ == "__main__":
    main()
