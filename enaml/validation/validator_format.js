//-----------------------------------------------------------------------------
// Copyright (c) 2013, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file COPYING.txt, distributed with this software.
//-----------------------------------------------------------------------------
//
//     JSON does not allow comments, so this file is marked as js.
//     However, it is describing a JSON specification.
//
//-----------------------------------------------------------------------------
// Validator Format
//-----------------------------------------------------------------------------
// This describes the format for specifying a client-side validator which
// validates user text input. The format is intentionally loose so that it
// may scale with new requirements as dictated by future use cases.
{
  // The type of this client-side validator. If a particular client does
  // not support this validator type, the validator will be ignored. This
  // field is required.
  "type": "<string>",

  // Different types of validators may require arguments to be supplied
  // to the client-side validator object. These are specified as key-value
  // pairs and depend upon the validator "type". This field is required.
  "arguments": {},

  // The message which should be displayed by the control when the
  // validator fails. The means by which this message is displayed,
  // or whether it is displayed at all, is implementation defined.
  // This field is optional.
  "message": "<string>"
}


//-----------------------------------------------------------------------------
// Currently Supported Validators
//-----------------------------------------------------------------------------
// The following fragments describe the currently supported validators.
// Only the required fields are described. The optional fields function
// exactly as described in the specification of the validator format.

// Regex Validator - uses a regular expression to validate text.
{
  "type": "regex",
  "arguments": {
    // The regex string to use for validating the text. The regex format
    // follows Python's regex rules. Only text which matches the regex
    // is considered valid.
    "regex": "<string>",
  }
}


// Int Validator - allows integer input within a value range
{
  "type": "int",
  "arguments": {
    // The number base to use with the range. Supported bases are
    // 2, 8, 10, and 16.
    "base": 2 | 8 | 10 | 16,

    // The base 10 lower bound of allowable values, inlcusive. Null
    // indicates no lower bound.
    "minimum": null,

    // The base 10 upper bound of allowable values, inclusive. Null
    // indicates no upper bound.
    "maximum": null,
  }
}


// Float Range Validator - allows float input within a value range
{
  "type": "float",
  "arguments": {
    // The lower bound of allowable values, inlcusive. Null indicates
    // no lower bound.
    "minimum": null,

    // The upper bound of allowable values, inclusive. Null indicates
    // no upper bound.
    "maximum": null,

    // Whether or not to allow exponents like '1e6' in the input.
    "allow_exponent": false,
  }
}

