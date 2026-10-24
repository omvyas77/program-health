select subject
from {{ source('config', 'gies_subjects') }}
