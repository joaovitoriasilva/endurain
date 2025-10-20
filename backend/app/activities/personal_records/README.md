# Personal Records (PRs) Module

This module implements automatic tracking of personal records (PRs) for fitness activities.

## Features

### Supported Activity Types

#### 🏃 Running (activity_type: 1, 2, 3, 34)
- **fastest_1km**: Fastest time to complete 1km
- **fastest_5km**: Fastest time to complete 5km
- **fastest_10km**: Fastest time to complete 10km
- **fastest_half_marathon**: Fastest time to complete 21.097km
- **fastest_marathon**: Fastest time to complete 42.195km
- **longest_distance**: Longest running distance
- **best_average_pace**: Best average pace (lower is better)

#### 🚴 Cycling (activity_type: 4, 5, 6, 7, 27, 28, 29, 35, 36)
- **fastest_5km**: Fastest time to complete 5km
- **fastest_20km**: Fastest time to complete 20km
- **fastest_40km**: Fastest time to complete 40km
- **longest_distance**: Longest cycling distance
- **max_power**: Maximum power output (watts)
- **best_normalized_power**: Best normalized power (FTP indicator)

#### 🏊 Swimming (activity_type: 8, 9)
- **fastest_50m**: Fastest time to complete 50m
- **fastest_100m**: Fastest time to complete 100m
- **fastest_200m**: Fastest time to complete 200m
- **fastest_400m**: Fastest time to complete 400m
- **fastest_1500m**: Fastest time to complete 1500m
- **longest_distance**: Longest swimming distance

#### 🏋️ Strength Training (activity_type: 19, 20)
- Placeholder for future implementation (requires activity_sets parsing)

## How It Works

### Automatic PR Detection
PRs are automatically checked and updated whenever:
1. A new activity is uploaded (GPX, TCX, or FIT file)
2. An activity is synced from Strava
3. An activity is synced from Garmin Connect

### Distance Tolerance
To ensure accurate PR tracking, distance-based PRs use a tolerance threshold:
- **Running/Cycling**: 2% tolerance (e.g., 4.9-5.1km counts as 5km)
- **Swimming**: 5% tolerance (pool distances can vary)

This prevents false PRs from longer activities where we don't have split data.

### Database Schema
```python
class PersonalRecord:
    id: int                    # Primary key
    user_id: int              # Foreign key to users table
    activity_id: int          # Foreign key to activities table
    activity_type: int        # Activity type (1=run, 4=ride, etc.)
    pr_date: datetime         # When the PR was set
    metric: str               # PR metric name (e.g., 'fastest_5km')
    value: Decimal            # PR value (time in seconds, distance in meters, etc.)
    unit: str                 # Unit of measurement ('seconds', 'meters', 'watts', etc.)
```

## API Endpoints

### GET /personal_records/user/{user_id}
Get all personal records for a user.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "activity_id": 456,
    "activity_type": 1,
    "pr_date": "2025-10-11T10:30:00",
    "metric": "fastest_5km",
    "value": "1200.50",
    "unit": "seconds"
  }
]
```

### POST /personal_records/user/{user_id}/recalculate
Recalculate all personal records for a user from scratch.

**Response:**
```json
{
  "message": "Personal records recalculated successfully"
}
```

## Initial Data Migration

To calculate PRs for existing activities, use the migration script:

```bash
# Migrate all users
cd backend/app
python -m activities.personal_records.migration

# Migrate specific user
python -m activities.personal_records.migration 123
```

## Database Migration

Run Alembic migration to create the personal_records table:

```bash
cd backend/app
alembic upgrade head
```

## Future Enhancements

1. **Strength Training PRs**: Parse activity_sets to track 1RM for specific exercises
2. **Segment PRs**: Track best times for specific route segments (like Strava segments)
3. **Power-based PRs**: Add 1-min, 5-min, 20-min power PRs for cycling
4. **Notifications**: Alert users when they set a new PR
5. **PR History**: Track historical PRs to see progression over time
6. **Stream-based PRs**: Calculate split times from activity streams for more accurate distance PRs
