select yearterm, term_flag
from {{ source('config', 'term_flags') }}
