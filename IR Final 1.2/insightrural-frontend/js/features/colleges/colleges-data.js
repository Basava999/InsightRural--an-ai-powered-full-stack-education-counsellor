// Mock data for Colleges feature
const CollegesData = {
    // Mock colleges database
    colleges: [
        {
            id: 1,
            name: "Indian Institute of Technology (IIT) Delhi",
            location: "Delhi",
            type: "Government",
            courses: ["B.Tech", "M.Tech", "PhD"],
            fees: "₹2-3 Lakhs/year",
            eligibility: "JEE Advanced, 12th with PCM",
            ruralQuota: "Yes, 14.5% seats reserved",
            placement: "Highest: ₹2 Cr, Average: ₹25 LPA"
        },
        {
            id: 2,
            name: "National Institute of Technology (NIT) Patna",
            location: "Patna, Bihar",
            type: "Government",
            courses: ["B.Tech", "M.Tech", "MCA", "MBA"],
            fees: "₹1.5-2 Lakhs/year",
            eligibility: "JEE Main, 12th with PCM",
            ruralQuota: "Yes, through JEE Main",
            placement: "Highest: ₹45 LPA, Average: ₹8 LPA"
        },
        {
            id: 3,
            name: "Rajiv Gandhi Institute of Petroleum Technology",
            location: "Raebareli, UP",
            type: "Government",
            courses: ["B.Tech Petroleum", "M.Tech", "PhD"],
            fees: "₹1-1.5 Lakhs/year",
            eligibility: "JEE Main, 12th with PCM",
            ruralQuota: "Special consideration for rural students",
            placement: "Highest: ₹30 LPA, Average: ₹7 LPA"
        },
        {
            id: 4,
            name: "Central University of South Bihar",
            location: "Gaya, Bihar",
            type: "Central University",
            courses: ["BA", "B.Sc", "B.Com", "B.Tech", "MA", "M.Sc"],
            fees: "₹20-50k/year",
            eligibility: "CUET, 12th pass",
            ruralQuota: "Reservation as per Government norms",
            placement: "Varied across departments"
        }
    ],
    
    // Common courses and eligibility
    courses: [
        {
            name: "Engineering (B.Tech)",
            duration: "4 years",
            eligibility: "12th with Physics, Chemistry, Mathematics (PCM)",
            entrance: "JEE Main, JEE Advanced, State CETs"
        },
        {
            name: "Medical (MBBS)",
            duration: "5.5 years",
            eligibility: "12th with Physics, Chemistry, Biology (PCB)",
            entrance: "NEET"
        },
        {
            name: "Commerce (B.Com)",
            duration: "3 years",
            eligibility: "12th in any stream (Commerce preferred)",
            entrance: "Mostly merit-based"
        },
        {
            name: "Arts (BA)",
            duration: "3 years",
            eligibility: "12th in any stream",
            entrance: "Mostly merit-based"
        },
        {
            name: "Science (B.Sc)",
            duration: "3 years",
            eligibility: "12th with Science subjects",
            entrance: "Mostly merit-based"
        }
    ],
    
    // Exam information
    exams: [
        {
            name: "JEE Main",
            purpose: "Engineering admissions in NITs, IIITs, GFTIs",
            eligibility: "12th with PCM, age limit: 25 years",
            application: "December-January",
            examDate: "January-April",
            website: "https://jeemain.nta.nic.in"
        },
        {
            name: "JEE Advanced",
            purpose: "Engineering admissions in IITs",
            eligibility: "Top 2.5 lakh rank holders in JEE Main",
            application: "April-May",
            examDate: "May",
            website: "https://jeeadv.ac.in"
        },
        {
            name: "NEET",
            purpose: "Medical admissions (MBBS/BDS)",
            eligibility: "12th with PCB, age limit: 25 years",
            application: "March-April",
            examDate: "May",
            website: "https://neet.nta.nic.in"
        },
        {
            name: "CUET",
            purpose: "Admissions to Central Universities",
            eligibility: "12th pass in any stream",
            application: "February-March",
            examDate: "May-July",
            website: "https://cuet.samarth.ac.in"
        }
    ],
    
    // Get a response based on user query
    getResponse(query) {
        const lowerQuery = query.toLowerCase();
        
        if (lowerQuery.includes('engineering') || lowerQuery.includes('iit') || lowerQuery.includes('nit')) {
            return this.getEngineeringResponse();
        } else if (lowerQuery.includes('medical') || lowerQuery.includes('neet') || lowerQuery.includes('mbbs')) {
            return this.getMedicalResponse();
        } else if (lowerQuery.includes('college') && lowerQuery.includes('list')) {
            return this.getCollegeList();
        } else if (lowerQuery.includes('exam') || lowerQuery.includes('entrance') || lowerQuery.includes('jee')) {
            return this.getExamInfo();
        } else if (lowerQuery.includes('course') || lowerQuery.includes('program')) {
            return this.getCourseInfo();
        } else if (lowerQuery.includes('fee') || lowerQuery.includes('cost')) {
            return this.getFeeInfo();
        } else if (lowerQuery.includes('rural') || lowerQuery.includes('quota') || lowerQuery.includes('reservation')) {
            return this.getRuralQuotaInfo();
        } else if (lowerQuery.includes('placement') || lowerQuery.includes('job') || lowerQuery.includes('salary')) {
            return this.getPlacementInfo();
        } else {
            return this.getGeneralCollegeInfo();
        }
    },
    
    // Specific response generators
    getEngineeringResponse() {
        return `For engineering, top options include:
        
🏛️ **IITs** (Indian Institutes of Technology) - Through JEE Advanced
🏛️ **NITs** (National Institutes of Technology) - Through JEE Main
🏛️ **State Government Colleges** - Through state CET exams
🏛️ **Private Colleges** - Through JEE Main or own entrance exams

**Key Exams:**
• JEE Main (for NITs, IIITs, GFTIs)
• JEE Advanced (for IITs)
• State CETs (for state colleges)

**Rural Student Support:** Most government colleges have reservation quotas. Some institutes like RGIPT have special provisions for rural students.`;
    },
    
    getMedicalResponse() {
        return `For medical courses (MBBS/BDS):

🏥 **Government Medical Colleges** - Through NEET, highly competitive
🏥 **Private Medical Colleges** - Through NEET, higher fees
🏥 **AIIMS** - Separate entrance (AIIMS UG) - now merged with NEET
🏥 **State Medical Colleges** - Through NEET with state quota

**Key Exam:** NEET (National Eligibility cum Entrance Test)

**Fee Structure:**
• Government colleges: ₹10,000 - ₹1 Lakh/year
• Private colleges: ₹5 Lakhs - ₹25 Lakhs/year

**Rural Quota:** Some states have rural area quotas in government medical colleges.`;
    },
    
    getCollegeList() {
        let response = "**Top colleges accessible to rural students:**\n\n";
        
        this.colleges.forEach(college => {
            response += `🏛️ **${college.name}** (${college.location})\n`;
            response += `   Type: ${college.type} | Courses: ${college.courses.join(", ")}\n`;
            response += `   Fees: ${college.fees} | Rural Quota: ${college.ruralQuota}\n\n`;
        });
        
        response += "You can ask about specific colleges for more details.";
        return response;
    },
    
    getExamInfo() {
        let response = "**Key entrance exams for higher education:**\n\n";
        
        this.exams.forEach(exam => {
            response += `📝 **${exam.name}**\n`;
            response += `   Purpose: ${exam.purpose}\n`;
            response += `   Eligibility: ${exam.eligibility}\n`;
            response += `   Application: ${exam.application}\n`;
            response += `   Exam Date: ${exam.examDate}\n\n`;
        });
        
        return response;
    },
    
    getCourseInfo() {
        let response = "**Popular courses after 12th:**\n\n";
        
        this.courses.forEach(course => {
            response += `🎓 **${course.name}** (${course.duration})\n`;
            response += `   Eligibility: ${course.eligibility}\n`;
            response += `   Entrance: ${course.entrance}\n\n`;
        });
        
        return response;
    },
    
    getFeeInfo() {
        return `**Fee structure for different college types:**

💰 **Government Colleges (IITs/NITs/Central Universities):**
• Tuition: ₹10,000 - ₹2 Lakhs/year
• Hostel: ₹20,000 - ₹50,000/year
• Total: ₹30,000 - ₹2.5 Lakhs/year

💰 **State Government Colleges:**
• Tuition: ₹5,000 - ₹50,000/year
• Hostel: ₹10,000 - ₹30,000/year
• Total: ₹15,000 - ₹80,000/year

💰 **Private Colleges:**
• Tuition: ₹50,000 - ₹10 Lakhs/year
• Hostel: ₹30,000 - ₹1 Lakh/year
• Total: ₹80,000 - ₹11 Lakhs/year

**Note:** Scholarships and education loans can significantly reduce the financial burden. Check the Scholarships section for more information.`;
    },
    
    getRuralQuotaInfo() {
        return `**Support for rural students in college admissions:**

✅ **Reservation Quotas:**
• SC: 15%
• ST: 7.5%
• OBC: 27%
• EWS: 10%

✅ **Special Provisions:**
• Some states have rural area quotas (e.g., Haryana, Punjab)
• Certain institutes like RGIPT have special consideration for rural students
• JEE Main/Advanced have relaxation in eligibility marks for reserved categories

✅ **Financial Support:**
• Fee waivers for economically weaker sections
• Scholarships specifically for rural students
• Free coaching for entrance exams in some states

**Tip:** Always check the specific reservation policies of each college and state.`;
    },
    
    getPlacementInfo() {
        return `**Placement statistics (approximate):**

🏆 **Top IITs (IIT Bombay/Delhi/Madras):**
• Highest package: ₹1-2 Crore/year
• Average package: ₹15-25 LPA
• Placement rate: 80-90%

🏆 **Other IITs & Top NITs:**
• Highest package: ₹30-70 LPA
• Average package: ₹8-15 LPA
• Placement rate: 70-85%

🏆 **State Government Colleges:**
• Highest package: ₹10-30 LPA
• Average package: ₹3-8 LPA
• Placement rate: 60-75%

🏆 **Private Colleges (Tier 2/3):**
• Highest package: ₹5-20 LPA
• Average package: ₹2-6 LPA
• Placement rate: 40-70%

**Note:** Placement statistics vary yearly and by branch. Computer Science typically has the highest placements.`;
    },
    
    getGeneralCollegeInfo() {
        return `I can help you with various college-related information:

• **College lists** - Top colleges for different streams
• **Courses** - Available programs and eligibility
• **Entrance exams** - JEE, NEET, CUET, etc.
• **Fee structure** - Costs for different types of colleges
• **Admission process** - Step-by-step guidance
• **Reservation policies** - Quotas for rural/SC/ST/OBC students
• **Placement records** - Job opportunities after graduation

What specific information are you looking for? You can also try one of the quick questions above!`;
    }
};