using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace ExamPrep.Models
{
    public partial class QuestionGroup
    {
        public QuestionGroup()
        {
            Questions = new HashSet<Question>();
        }
        
        public int Id {get; set; }
        public int? ProgramId {get; set;}
        public int? ProgramChapterId { get; set; }
        public int? QuestionTypeId {get: set;}
        public string? LinkToObject {get; set;}
        public string? ObjectType { get; set; }
        public string GroupText {get; set;}
        public string GroupTitle { get; set; }
        public string Explanation { get; set; }
        public DateTime CreatedDate {get; set;} = DateTime.UtcNow;
        
        public virtual Programs Program {get; set;}
        public virtual QuestionType QuestionType {get; set;}
        public virtual Icollection<Question> Questions{get; set;}

    }
}