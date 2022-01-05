var assert = require("assert")
// Given an array of numbers, return a new array so that positive and negative
// numbers alternate. You can assume that 0 is a positive number. Within the
// positive and negative numbers, you must keep their relative order. You are 
// guaranteed the number of positive and negative numbers will not differ by more 
// than 1.

// =====Example 1
// Input: [1, -3, -8, -5, 10]
// Output: [-3, 1, -8, 10, -5]
// Explanation: We have alternated positive and negative numbers. Notice that the
// negative numbers appear in the same relative order (-3, -8, -5) and the positive
// numbers appear in the same order as well (1, 10).

// =====Example 2
// Input: [3, 0, 0, -5, -2]
// Output: [3, -5, 0, -2, 0]
// Explanation: We have alternated positive and negative numbers. Notice they appear
// in the same relative order.

// =====Example 3
// Input: [0, -3, 3, -1, 1, -1]
// Output #1: [0, -3, 3, -1, 1, -1]
// Output #2: [-3, 0, -1, 3, -1, 1]
// Explanation: There are 2 possible answers which satisfy the problem's constraints.
// We can start with either positive or negative

// =====Example 4
// Input numArray: []
// Output numArray: []
// Explanation: Empty array...

const altNumbers = (numArray) => {
    // Note that I haven't even used JavaScript before - I'm sure my style is massively off or I've missed something

    // Idea is to iterate through numArray add elements to two new arrays:
    //  - One that has all the positive numbers + zero
    //  - One that has all the negative numbers
    let pos = [];
    let neg = [];

    // Iterate through numArray
    for (let i = 0; i < numArray.length; i++) {
        if (numArray[i] >= 0) {
            // It's positive or zero, add to 'pos'
            pos.push(numArray[i]);
        } else {
            // Must be negative if it gets here
            neg.push(numArray[i]);
        }
    }

    // Check if the lengths are within one of each other.
    // If they're not, there's a problem since it's impossible for them to alternate -> throw some error
    const lengthDiff = Math.abs(pos.length - neg.length);
    if (lengthDiff > 1) {
        throw new Error("The positive/negative numbers are imbalanced by more than 1. #positives = " + String(pos.length) + ", #negatives = " + String(neg.length));
    }

    // Cool, it's a valid input.
    
    // If there are more positive numbers, we must start with a positive number.
    // If there are more negative numbers, we must start with a negative number.
    // If there are equal amounts of positive and negative numbers, we don't care which starts. Default to positive.    
    let nextIsPos = (pos.length >= neg.length);

    // Make a new, empty array and iterate through the pos and neg arrays
    let ans = [];
    let posCounter = 0;
    let negCounter = 0;
    while (ans.length != numArray.length) {
        if (nextIsPos) {
            // Add a positive
            ans.push(pos[posCounter]);
            posCounter++;
        } else {
            // Add a negative
            ans.push(neg[negCounter]);
            negCounter++;
        }
        
        // Flip nextIsPos to whatever it isn't
        nextIsPos = !nextIsPos;
    }

    // Yay done, return it
    return ans;
}

module.exports = { altNumbers } // Do not modify this line

// ====================TESTS====================
// Some tests to help you check your progress. Simply run your code with
// node easy.js
// If successful, no output should appear. If unsuccessful, you should see 
// assertion errors being thrown.

let array1 = [1, -3, -8, -5, 10]
array1 = altNumbers(array1)
const answer1 = [-3, 1, -8, 10, -5]
for (let i = 0; i < array1.length; i++) {
    assert(array1[i] === answer1[i])
}

let array2 = [3, 0, 0, -5, -2]
array2 = altNumbers(array2)
const answer2 = [3, -5, 0, -2, 0]
for (let i = 0; i < array2.length; i++) {
    assert(array2[i] === answer2[i])
}

let array3 = [0, -3, 3, -1, 1, -1]
array3 = altNumbers(array3)
const answer3a = [0, -3, 3, -1, 1, -1]
const answer3b = [-3, 0, -1, 3, -1, 1]
if (array3[0] === 0) {
    for (let i = 0; i < array3.length; i++) {
        assert(array3[i] === answer3a[i])
    }
} else if (array3[0] == -3) {
    for (let i = 0; i < array3.length; i++) {
        assert(array3[i] === answer3b[i])
    }
} else {
    assert(false)
}

let array4 = []
array4 = altNumbers(array4)
assert(array4.length === 0)

let array5 = [3,2,1,-1,-2,-3,-4]
array5 = altNumbers(array5)
const answer5 = [-1, 3, -2, 2, -3, 1, -4]
for (let i = 0; i < array5.length; i++) {
    assert(array5[i] === answer5[i])
}

let array6 = [5,-1,-2,-3,-4,0,3]
array6 = altNumbers(array6)
const answer6 = [-1, 5, -2, 0, -3, 3, -4]
for (let i = 0; i < array6.length; i++) {
    assert(array6[i] === answer6[i])
}

// My own tests that're built to fail.
// Has unbalanced number of positives and negatives.
let array7 = [5,-1,-2,-3,4,0,3,7]
try {
    array7 = altNumbers(array7)
} catch (error) {
    console.log("As expected, altNumbers failed with error on array7. " + error + "\n");
}

let array8 = [-5,9,-1,-2,-3,-4,0,3]
try {
    array8 = altNumbers(array8)
} catch (error) {
    console.log("As expected, altNumbers failed with error on array8. " + error + "\n");
}