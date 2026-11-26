def time_to_minutes(hhmm):
    """Convert 'HH:MM' string into minutes from midnight."""
    parts = hhmm.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def intervals_overlap(start_a, end_a, start_b, end_b):
    """Return True if two [start, end) time intervals in minutes overlap."""
    return start_a < end_b and start_b < end_a


def find_scheduling_conflicts(schedule_list):
    """
    Detect overlapping events at the same venue or teams scheduled in overlapping events.
    Each tuple in schedule_list: (event_id, event_name, venue, start_hhmm, end_hhmm, teams_tuple)
    """
    conflicts = []
    n = len(schedule_list)

    for i in range(n):
        ev1 = schedule_list[i]
        s1 = time_to_minutes(ev1[3])
        e1 = time_to_minutes(ev1[4])

        for j in range(i + 1, n):
            ev2 = schedule_list[j]
            s2 = time_to_minutes(ev2[3])
            e2 = time_to_minutes(ev2[4])

            if intervals_overlap(s1, e1, s2, e2):
                # Same venue clash
                if ev1[2] == ev2[2]:
                    conflicts.append(
                        f"Venue Clash at '{ev1[2]}': {ev1[0]} ({ev1[1]}, {ev1[3]}-{ev1[4]}) "
                        f"overlaps with {ev2[0]} ({ev2[1]}, {ev2[3]}-{ev2[4]})."
                    )

                # Shared team clash
                shared_teams = []
                for tm in ev1[5]:
                    if tm in ev2[5] and tm not in shared_teams:
                        shared_teams.append(tm)

                if shared_teams:
                    conflicts.append(
                        f"Team Clash ({', '.join(shared_teams)}): {ev1[0]} ({ev1[1]}, {ev1[3]}-{ev1[4]}) "
                        f"overlaps with {ev2[0]} ({ev2[1]}, {ev2[3]}-{ev2[4]})."
                    )

    return conflicts


def aggregate_team_points(teams_list, score_entries):
    """
    Aggregate points per team from score_entries.
    Each score_entry tuple: (event_id, team_name, points, rank_in_event)
    """
    totals = {}
    for tm in teams_list:
        totals[tm] = {
            "team": tm,
            "events_played": 0,
            "total_points": 0,
            "gold_count": 0,
            "silver_count": 0,
        }

    for entry in score_entries:
        _, tm, pts, ev_rank = entry
        if tm in totals:
            totals[tm]["events_played"] += 1
            totals[tm]["total_points"] += pts
            if ev_rank == 1:
                totals[tm]["gold_count"] += 1
            elif ev_rank == 2:
                totals[tm]["silver_count"] += 1

    return list(totals.values())


def rank_teams(team_stats):
    """Rank teams by total points, then gold medals, silver medals, and team name."""
    ordered = list(team_stats)
    n = len(ordered)

    for i in range(n):
        for j in range(i + 1, n):
            a = ordered[j]
            b = ordered[i]
            swap = False

            if a["total_points"] != b["total_points"]:
                swap = a["total_points"] > b["total_points"]
            elif a["gold_count"] != b["gold_count"]:
                swap = a["gold_count"] > b["gold_count"]
            elif a["silver_count"] != b["silver_count"]:
                swap = a["silver_count"] > b["silver_count"]
            else:
                swap = a["team"] < b["team"]

            if swap:
                ordered[i], ordered[j] = ordered[j], ordered[i]

    for idx, rec in enumerate(ordered):
        rec["final_rank"] = idx + 1

    return ordered


def print_report(schedule_list, conflicts, ranked_teams):
    """Display event schedule, detected conflicts, and final team standings."""
    print("=" * 92)
    print("MULTI-EVENT SPORTS SCHEDULE")
    print("=" * 92)
    print(f"{'ID':<6} {'Event Name':<22} {'Venue':<16} {'Time':<13} {'Participating Teams'}")
    print("-" * 92)
    for ev in schedule_list:
        ev_id, name, venue, start, end, teams_t = ev
        print(f"{ev_id:<6} {name:<22} {venue:<16} {start + '-' + end:<13} {', '.join(teams_t)}")

    print("\n--- Scheduling Conflicts ---")
    if not conflicts:
        print("No scheduling conflicts found.")
    else:
        for c in conflicts:
            print("CONFLICT:", c)

    print("\n" + "=" * 92)
    print("FINAL TEAM STANDINGS")
    print("=" * 92)
    print(f"{'Rank':>4} {'Team Name':<18} {'Events':>7} {'Gold':>6} {'Silver':>7} {'Total Points':>13}")
    print("-" * 92)
    for t in ranked_teams:
        print(
            f"{t['final_rank']:>4} {t['team']:<18} {t['events_played']:>7} "
            f"{t['gold_count']:>6} {t['silver_count']:>7} {t['total_points']:>13}"
        )
    print("=" * 92 + "\n")


def main():
    # List of tuples: (event_id, event_name, venue, start_time, end_time, teams_tuple)
    schedule = [
        ("E01", "100m Relay", "Main Track", "09:00", "10:30", ("Falcons", "Titans", "Vipers", "Hawks")),
        ("E02", "Basketball Semifinal", "Indoor Court", "09:30", "11:00", ("Falcons", "Eagles")),
        ("E03", "400m Hurdles", "Main Track", "10:00", "11:15", ("Titans", "Eagles", "Hawks")),
        ("E04", "Table Tennis Final", "Hall B", "11:30", "12:30", ("Vipers", "Eagles")),
    ]

    teams = ["Falcons", "Titans", "Vipers", "Hawks", "Eagles"]

    # List of score tuples: (event_id, team_name, points, event_rank)
    scores = [
        ("E01", "Falcons", 10, 1),
        ("E01", "Titans", 7, 2),
        ("E01", "Vipers", 5, 3),
        ("E01", "Hawks", 3, 4),
        ("E02", "Eagles", 10, 1),
        ("E02", "Falcons", 6, 2),
        ("E03", "Hawks", 10, 1),
        ("E03", "Eagles", 7, 2),
        ("E03", "Titans", 5, 3),
        ("E04", "Vipers", 10, 1),
        ("E04", "Eagles", 6, 2),
    ]

    conflicts = find_scheduling_conflicts(schedule)
    aggregated = aggregate_team_points(teams, scores)
    ranked = rank_teams(aggregated)
    print_report(schedule, conflicts, ranked)


if __name__ == "__main__":
    main()
