/*
Regular expression for ISO 8601 datetime format.

NOTE: This regex is not strict. For example, a datetime with month is greater than 12 passes this regex.

Translated from: regex_iso8601_datetime.py
*/

// minimalist form (no useful groups, for checking-only)
const regex_iso8601_datetime_minimalist = /^\d{4}(?:(-?)\d{2}\1\d{2}|(-?)W\d{2}\2[1-7]|-?\d{3})T\d{2}(?:(:?)\d{2}(?:\3\d{2}(?:\.\d{1,6})?)?)?(?:Z|[+\-\u2212]\d{2}(?::?\d{2}(?::?\d{2})?)?)?$/;

// expanded(verbose) form (for parsing)
const regex_iso8601_datetime = /^(?<date>(?<year>\d{4})(?:(?<ymd_hyphen>-?)(?<month>\d{2})\k<ymd_hyphen>(?<day>\d{2})|(?<ywd_hyphen>-?)W(?<week>\d{2})\k<ywd_hyphen>(?<weekday>[1-7])|-?(?<ordinalday>\d{3})))T(?<time>(?<hour>\d{2})(?:(?<hms_colon>:?)(?<minute>\d{2})(?:\k<hms_colon>(?<second>\d{2})(?:\.(?<microsecond>\d{1,6}))?)?)?)(?<tzinfo>Z|(?<tzsign>[+\-\u2212])(?<tzhour>\d{2})(?::?(?<tzminute>\d{2})(?::?(?<tzsecond>\d{2}))?)?)?$/;

function* product(...iterables) {
    if (iterables.length === 0) {
        yield [];
    } else {
        let [first_iterable, ...last_iterables] = iterables;
        for (let item of first_iterable) {
            for (let last_items of product(...last_iterables)) {
                yield [item].concat(last_items);
            }
        }
    }
}

var test_cases_date = ['2020-01-02', '20200102', '2020-W01-2', '2020W012', '2020123', '2020-123'];
var test_cases_time = ['12:34:56', '123456', '12:34:56.123456', '123456.123456'];
var test_cases_tzinfo = ['', 'Z', '+12:34', '+1234', '+12','+123456'];

for (let [test_case_date, test_case_time, test_case_tzinfo] of product(test_cases_date, test_cases_time, test_cases_tzinfo)) {
    let test_case = `${test_case_date}T${test_case_time}${test_case_tzinfo}`;
    let matches = test_case.match(regex_iso8601_datetime);
    if (matches) {
        console.log(`${test_case}: date=${matches.groups.date}, time=${matches.groups.time}, tzinfo=${matches.groups.tzinfo}`);
    } else {
        console.log(`${test_case}: not matched`);
    }
}
